function copyToClipboard(){
    let text_from_element = $('#id_transaction').text()
    id_transaction = text_from_element.toLowerCase().replace('id:', '');
    navigator.clipboard.writeText(id_transaction);
}