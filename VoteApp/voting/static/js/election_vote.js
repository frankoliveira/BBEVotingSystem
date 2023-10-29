//import * as base from './base';

function get_candidacy_details() {
    //const Url = `${base.host}:${base.port}${base.VoteAppApiEndpoints.DetalhesCandidatura}/${1}`
    const Url = "http://127.0.0.1:8080/eleicoes/candidatura/1/"
    console.log(Url);
    $.ajax({
        url: Url,
        type: "GET",
        success: function(result){
            console.log(result)
        },
        error:function(error){
            console.log(`Error: ${error}`)
        }
    })
}