function enterInUrlForm(element){
    document.getElementById("id_url").setAttribute("value", element.textContent)
}

function radio(x){
    if (x == 0){
        document.getElementById('url').style.display='block';
        document.getElementById('keyword').style.display='none';
    }
    else{
        document.getElementById('keyword').style.display='block';
        document.getElementById('url').style.display='none';
    }
}

function loading(){
    document.getElementById('loader').style.visibility = 'visible';
}


