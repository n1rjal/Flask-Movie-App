

function favadder(idofclickedbutton){
    let xhr= new XMLHttpRequest();
    let buttonclicked=idofclickedbutton;

    idofclickedbutton=idofclickedbutton.split(":");

    let countnumber=idofclickedbutton[1];
    
    idofclickedbutton=idofclickedbutton[0];
    
    //and check if works in mobile or not
    //change this during porduction
    let url="http://localhost:5000/addtofav";
    xhr.open('POST',url);
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
   /* document.addEventListener("DOMContentLoaded", function(event) { 
        });
    */
    let title=document.getElementById("title"+countnumber).innerText;
    let Poster=document.getElementById("card-img-top"+countnumber).src;
    let type=document.getElementById("type"+countnumber).innerText;
    let imdb=document.getElementById("imdb"+countnumber).href;
    let year=document.getElementById("year"+countnumber).innerText;

    
    //now fixing the id
    idofclickedbutton = idofclickedbutton + countnumber;
    
    xhr.send(`title=${title}&year=${year}&type=${type}&imdb=${imdb}&poster=${Poster}`);
    xhr.onreadystatechange=function(){

        resp=JSON.parse(xhr.responseText);
        console.log(resp);
        setTimeout(()=>{
            if (resp.code=="sucess"){
                button=document.getElementById(buttonclicked);
                button.innerText="Added to Favourite";
                button.disabled=true;
            }
            else{
                if  (resp.code=="signup"){
                    location.replace("http://localhost:5000/useraction")
                }
            }
        },5000);
        
    };
    
}
