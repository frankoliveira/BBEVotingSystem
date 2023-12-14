#Models
from .models import Orderer
from transaction.models import Transaction, TransactionBlock
from block.models import Block
from blockchain.models import Blockchain
from peer.models import Peer
from security.CustomRSA import CustomRSA
from django.core.paginator import Paginator

#Serializers
from transaction.serializers import TransactionSerializer, TransactionBlockSerializer
from block.serializers import BlockSerializer

#Other
import json, time, base64
from hashlib import sha256
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import api_view
import threading

@api_view(['POST']) 
def pending_transaction(request, format=None):
    '''
    Create a transaction with input from voting app
    Or receive a created transaction from a publishing node
    '''
    if request.method == 'POST':
        remote_peer: Peer = Peer.get_peer_by_id(id=request.data["peer_id"])
        
        if remote_peer==None:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)
        
        if remote_peer.is_publishing_node and remote_peer.authorized:
            transaction_serializer = TransactionSerializer(data=request.data["transaction"])

            if transaction_serializer.is_valid():
                transaction_serializer.save()
                return Response("accepted", status=status.HTTP_201_CREATED)
            
            return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif remote_peer.authorized:
            input = request.data['input']
            id = sha256(input.encode('utf-8')).hexdigest()
            origin = request.data['origin']
            signature = request.data['signature']
            if Transaction.check_if_exist(id=id)==False and TransactionBlock.check_if_exist(id=id)==False:
                transaction = Transaction.objects.create(
                    id = id,
                    input = input,
                    timestamp = datetime.now(),
                    origin = origin,
                    signature = signature
                )

                transaction_serializer = TransactionSerializer(instance=transaction)
                Orderer.broadcast_pending_transaction(transaction_serializer.data)
                return Response(transaction_serializer.data, status=status.HTTP_201_CREATED)
            return Response(data='Transação inválida', status=status.HTTP_400_BAD_REQUEST)

#inicia o consenso
@api_view(['GET']) 
def create_consensus_block(request, format=None):
    '''
    Essa lógica será executada de alguma forma pelo líder
    Aqui se inicia a proposta de bloco pelo líder
    '''
    if request.method == 'GET':
        try:
            new_block = Orderer.propose_block()
            if new_block:
                block_serializer = BlockSerializer(instance=new_block)
                return Response(data=block_serializer.data, status=status.HTTP_201_CREATED)
            return Response(data='Não há transações pendentes', status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(data=f"Erro na solicitação ccb:{ex}", status=status.HTTP_400_BAD_REQUEST)
        
#pre-prepare/ essse era o prepare
@api_view(['POST'])
def pre_prepare(request, format=None):
    """
    Recebe o novo bloco do Líder na fase de pré-prepare
    """
    print('pré-prepare acionado')
    if request.method == 'POST':
        try:
            orderer = Orderer.get_instance()
            remote_peer: Peer = Peer.get_peer_by_id(id=request.data["peer_id"])

            if remote_peer!=None and remote_peer.is_publishing_node and remote_peer.id==orderer.consensus_leader_id:
                block_serializer = BlockSerializer(data=request.data["block"])
                
                if block_serializer.is_valid():
                    pre_prepare_accepted = True
                    consensus_view = int(request.data["pre_prepare"]["view"])
                    consensus_number = int(request.data["pre_prepare"]["number"])
                    consensus_block_hash = request.data["pre_prepare"]["block_hash"]
                    signature = base64.b64decode(request.data["signature"])
                    bytes_block = json.dumps(block_serializer.data).encode('utf-8')
                    bytes_pre_prepare: bytes = json.dumps(request.data["pre_prepare"]).encode('utf-8')

                    if consensus_view != orderer.consensus_view:
                        pre_prepare_accepted = False
                        print("pre-prepare recusado: view diferente")

                    if Blockchain.get_last_block().id+1 != consensus_number:
                        pre_prepare_accepted = False
                        thread_check_for_blockchain_update = threading.Thread(target=orderer.check_for_blockchain_update)
                        thread_check_for_blockchain_update.start()
                        print("pre-prepare recusado: numero incorreto")
                    if orderer.check_hash(data=bytes_block, hash=consensus_block_hash) == False:
                        pre_prepare_accepted = False
                        print("pre-prepare recusado: hash incorreto")

                    if orderer.verify_signature(public_key=remote_peer.get_public_key(), signature=signature, message=bytes_pre_prepare) == False:
                        pre_prepare_accepted = False
                        print("pre-prepare recusado: falha na assinatura")

                    if orderer.verifify_merkle_root(transaction_dicts=json.loads(block_serializer.data['transactions']), 
                                                    merkle_root=block_serializer.data['merkle_root']) == False:
                        pre_prepare_accepted = False
                        print("pre-prepare recusado: falha na merkle root")

                    if pre_prepare_accepted:
                        print("pré-prepare aceito")
                        orderer.reset_consensus_values()
                        orderer.consensus_block_dict = block_serializer.data
                        orderer.consensus_number = consensus_number
                        orderer.consensus_block_hash = consensus_block_hash
                        print('enviando prepare')
                        orderer.send_prepare()
                        return Response(data='accepted', status=status.HTTP_200_OK)
                    return Response(data='refused', status=status.HTTP_400_BAD_REQUEST)
                return Response(block_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data='refused', status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(f'pre-prepare-error: {ex}')
            return Response(data=f'Error: {ex}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#prepare/
@api_view(['POST'])
def prepare(request, format=None):
    '''
    Retorna mensagem de prepare caso o pré-prepare esteja ok
    '''
    print('prepare acionado')
    if request.method == 'POST':
        remote_peer: Peer = Peer.get_peer_by_id(id=request.data["peer_id"])
        orderer = Orderer.get_instance()
        if remote_peer!=None and remote_peer.is_publishing_node:
            prepare_accepted = True
            consensus_view = int(request.data["prepare"]["view"])
            consensus_number = int(request.data["prepare"]["number"])
            consensus_block_hash = request.data["prepare"]["block_hash"]
            signature = base64.b64decode(request.data["signature"])
            bytes_prepare: bytes = json.dumps(request.data["prepare"]).encode('utf-8')

            if orderer.verify_signature(public_key=remote_peer.get_public_key(), signature=signature, message=bytes_prepare) == False:
                prepare_accepted = False
                print("pre-prepare recusado: falha na assinatura")

            if consensus_view != orderer.consensus_view:
                prepare_accepted = False
                print("prepare recusado: view diferente")

            if consensus_number != orderer.consensus_number:
                prepare_accepted = False
                print("prepare recusado: numero diferente")

            if consensus_block_hash != orderer.consensus_block_hash:
                prepare_accepted = False
                print("prepare recusado: hash incorreto")
            
            if prepare_accepted:
                print("prepare aceito")
                orderer.consensus_received_prepares += 1
                if orderer.consensus_received_prepares >= 1 and orderer.consensus_sent_commit==False:
                    print('enviando commit')
                    Orderer.send_commit()
                return Response(data='accepted', status=status.HTTP_200_OK)
            
            return Response(data='refused', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data='refused', status=status.HTTP_400_BAD_REQUEST)

#commit/
@api_view(['POST'])
def commit(request, format=None):
    '''
    Recebe resultado dos demais peers
    '''
    print('commit acionado')
    if request.method == 'POST':
        remote_peer: Peer = Peer.get_peer_by_id(id=request.data["peer_id"])
        orderer = Orderer.get_instance()

        if remote_peer!=None and remote_peer.is_publishing_node:
            commit_accepted = True
            consensus_view = int(request.data["commit"]["view"])
            consensus_number = int(request.data["commit"]["number"])
            consensus_block_hash = request.data["commit"]["block_hash"]
            signature = base64.b64decode(request.data["signature"])
            bytes_commit: bytes = json.dumps(request.data["commit"]).encode('utf-8')

            if orderer.verify_signature(public_key=remote_peer.get_public_key(), signature=signature, message=bytes_commit) == False:
                commit_accepted = False
                print("commit recusado: falha na assinatura")

            if consensus_view != orderer.consensus_view:
                commit_accepted = False
                print("commit recusado: view diferente")

            if consensus_number != orderer.consensus_number:
                #verificar intervalo do número
                commit_accepted = False
                print("prepare recusado: numero diferente")

            if commit_accepted:
                print("commit aceito")
                orderer.consensus_received_commits += 1
                if orderer.consensus_is_achieved == False and orderer.consensus_received_commits >= 1:
                    print('decidindo bloco')
                    Orderer.decide()
                return Response(data='accepted', status=status.HTTP_200_OK)

            return Response(data='refused', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_confirmed_transaction(request, pk, format=None):
    """
    Lista de blocos.
    """
    id_transaction = pk
    if request.method == 'GET':
        try:
            transaction = {
                "transaction": None
            }
            transaction_block = TransactionBlock.get_element_by_id(id_transaction=id_transaction)
            if transaction_block:
                block = Blockchain.get_block(id=transaction_block.id_block)
                transactions_list: list = json.loads(block.transactions)
                transaction['transaction'] = transactions_list[transaction_block.position]
            return Response(data=transaction, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(data=f'Erro: {ex}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def get_last_block_id(request, format=None):
    if request.method == 'GET':
        id_block = None
        block = Blockchain.get_last_block()
        if block:
            id_block = block.id
        return Response(data={"id": id_block}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_block(request, pk, format=None):
    if request.method == 'GET':
        id = int(pk)
        block = None
        block = Blockchain.get_block(id=id)
        block_serializer_data = None
        if block:
            block_serializer_data = BlockSerializer(instance=block).data

        return Response(data={"block": block_serializer_data}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def teste(request, format=None):
    if request.method == 'GET':
        Orderer.get_instance().check_for_blockchain_update()
        return Response(data="ok", status=status.HTTP_200_OK)