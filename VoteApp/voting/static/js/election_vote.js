//import * as base from './base';

function process_input(event, id_election){
    console.log(event.target)
    input_value = event.target.value
    //restrição de inteiros como entrada
    event.target.value = input_value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1')

    if (event.target.name && event.target.value.length>0){
        id_position = Number(event.target.name)
        position_answer = Number(event.target.value)

        get_candidacy_details(id_position, position_answer, id_election)
    }
    else if (event.target.value.length===0){
        id_position = Number(event.target.name)
        $(`#position-${id_position}-answer-info`).html(`Informe sua escolha`)
    }
}


function get_candidacy_details(id_position, candidacy_number, id_election) {
    const Url = `http://127.0.0.1:8080/eleicoes/candidatura/detalhes`
    /*$.ajaxSetup({
        headers: { 'X-CSRFToken': $.cookie('csrftoken')}
    })*/
    $.ajax({
        type: "POST",
        url: Url,
        headers: { 'X-CSRFToken': $.cookie('csrftoken')},
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify({
            id_election: id_election,
            number: candidacy_number
        }),
        success: function(result){
            mount_result(result, id_position)
        },
        error:function(error){
            console.log(`Error: ${error}`)
            $(`#position-${id_position}-answer-info`).html(`Opção inválida`)
        }
    })
};

function mount_result(api_result, id_position) {
    if (api_result.type === 1) {
        $(`#position-${id_position}-answer-info`).html(`
            <img class="rounded-circle"  src="${api_result.candidates[0].image}"  style="height: 50px; width: 50px;">
            <p>${api_result.name}</p>`)
    }
    else if (api_result.type === 2) {
        $(`#position-${id_position}-answer-info`).html(`
            <p>${api_result.name}</p>`)
    }
}

/*
function update_candidacy_details(event) {
    //console.log('oi')
    //console.log(event.target)

    position_id = null
    position_answer = null

    if(event.target.name && event.target.value){
        position_id = Number(event.target.name)
        position_answer = Number(event.target.value)
    }

    get_candidacy_details(position_id, position_answer)
}

function get_candidacy_details(position_id, candidacy_number) {
    //const Url = `${base.host}:${base.port}${base.VoteAppApiEndpoints.DetalhesCandidatura}/${1}`
    const Url = `http://127.0.0.1:8080/eleicoes/candidatura/${candidacy_number}/`
    console.log(Url);
    $.ajax({
        url: Url,
        type: "GET",
        success: function(result){
            console.log("sucesso")
            console.log(result)
            $(`#position-${position_id}-answer-info`).html(`
            <img class="rounded-circle"  src="${result.candidates[0].image}"  style="height: 50px; width: 50px;">
            <p>${result.name}</p>`)
        },
        error:function(error){
            console.log(`Error: ${error}`)
            $(`#position-${position_id}-answer-info`).html(`Opção inválida`)
        }
    })
};
*/