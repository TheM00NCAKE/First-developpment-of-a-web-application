/*///////////////////////////
Petite parenthèse : la Guadeloupe est une région "spéciale" dans le code : 
Chaque région est défini par un seul polygone <path> dans un groupe <g (avec un id)>, mais la Guadeloupe est composé de plusieurs polygones 
différents. Le code était censé spécifique à un seul polygone pour chaque évènement, mais vu que j'y arrive pas MDR, il y a des lignes 
spécifiques pour la région de la Guadeloupe (identifié par ses polygones de classe régions ET 'Gua')*/
var region_clique = "";
var departement_clique = ""; 
//style css permettant de faire un zoom
var style = {
    transform: 'scale(2.5)',
    transition: 'transform 0.2s ease-in',
};
//dict contenant les coordonnées du point d'origine du zoom de chaque région 
var TOrigin = { HautsDeFrance: '580px 0px', Normandie: '430px 50px', Bretagne: '210px 130px', GrandEst: '660px 100px', NouvelleAquitaine: '400px 420px', Occitanie: '500px 590px', IleDeFrance: '560px 100px', CentreValdeLoire: '500px 220px', PaysDeLaLoire: '360px 200px', BourgogneFrancheComté: '660px 200px', AuvergneRhôneAlpes: '660px 400px', ProvenceAlpesCôteDazur: '690px 500px', Corse: '900px 600px',Guyane_973:'0px 0px',Mayotte_976:'0px 90px',LaReunion_974:'0px 310px',Martinique_972:'0px 470px',Guadeloupe_972:'0px 600px'}; //x y
var dezoom = {
    transform: 'scale(1)',
    transition: 'transform 0.1s ease-out',
    willChange: 'transform'
};
/*HTML pour faire apparaître le symbole de chargement */
var test='<div id="load"><div id="square"></div><div id="square2"></div><div id="cercle"><div class="ball"></div></div><div id="cercle2"><div class="ball"></div></div></div>';
var deptss = $(); 
var couleurs={color_region:'#f5f5fe',color_departement:'#f5f5fe',color_reg_mouseover:'#b2d3fb',color_reg_clique:'#cbcbfa',color_dept_clique:'#4472c4',color_dept_mouseover:'#94baff', color_nuit:'#37474f'};
var url="";
//////////////////////////:Code pour le tableau
const compare = (ids, asc) => (row1, row2) => {
  const tdValue = (row, ids) => row.children[ids].textContent;
  const tri = (v1, v2) =>
    v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2)
      ? v1 - v2
      : v1.toString().localeCompare(v2);

  return tri(
    tdValue(asc ? row1 : row2, ids),
    tdValue(asc ? row2 : row1, ids)
  );
};

function tri(){
  const table = document.querySelector('table');
  const tbody = table.querySelector('tbody');
  const thx = table.querySelectorAll('th');
  const trxb = tbody.querySelectorAll('tr');

  thx.forEach((th, idx) => {
    th.addEventListener('click', function () {
      const asc = this.asc = !this.asc;
      const sortedRows = Array.from(trxb).sort(compare(idx, asc));
      sortedRows.forEach(row => tbody.appendChild(row));
    });
  });
}

//fonction pour envoyer les données sur flask 
function envoie(zone,id){
    document.getElementById('tableau_contenu').innerHTML=test;
    document.getElementById('jauge').innerHTML="";
    var annee_choisi=document.getElementById('annee').value;
    var service=document.getElementById('service').value;
    var search=document.getElementById('barre_filtrage').value;
    service_choisi=service.split(':');
    if (id=='gua'){
        url=`/Update_tableau?zone=Guadeloupe&annee=${encodeURIComponent(annee_choisi)}&service=${encodeURIComponent(service_choisi[0])}&Lservice=${encodeURIComponent(service_choisi[1])}`;
    }else{
        url=`/Update_tableau?zone=${encodeURIComponent(zone)}&search=${encodeURIComponent(search)}&annee=${encodeURIComponent(annee_choisi)}&service=${encodeURIComponent(service_choisi[0])}&Lservice=${encodeURIComponent(service_choisi[1])}`;
    }
        fetch(url)
        .then(resp => resp.text())
        .then(html => {
            const parts = html.split("|");
            document.getElementById('tableau_contenu').innerHTML = parts[0];
            if (id=="b"){
                var data= parseFloat(parts[1]);
                jauge([data]);
                $(".switch2 .slider").css('opacity','1');
                $(".switch2 .slider").css('cursor','pointer');
            }
            tri()
            fetch('/static/graph_data_region.json')
                .then(resp => resp.json())
                .then(data => {
                    graphiques(data.noms, data.valeurs,Object.keys(data.evolution),Object.values(data.evolution));
                });
    });
}
function avant_envoie(x){
    if(departement_clique!="") {
        envoie(departement_clique.slice(1),"");     
    }else if (region_clique!=""){
        envoie(region_clique.slice(1),"");
    }else if (x=='a'){
        envoie(region_clique.slice(1),"b");
    }
}

document.addEventListener('DOMContentLoaded', () => {
  tri();
});
/////////////////////////////Fin code tableau
function jauge(val){
    if (!isNaN(val)){
        // set the gauge type
        var gauge = anychart.gauges.linear();
        // set the data for the gauge
        gauge.data(val);
        // set the layout
        gauge.layout('horizontal');
        // create a color scale
        var scaleBarColorScale = anychart.scales.ordinalColor().ranges(
        [{from: -10,to: 0,color: ['#d5d5da', '#d5d5da']},
        {from: 0,to: 25,color: ['#D81E05', '#EB7A02']},
        {from: 25,to: 50,color: ['#EB7A02', '#FFD700']},
        {from: 50,to: 75,color: ['#FFD700', '#CAD70b']},
        {from: 75,to: 100,color: ['#CAD70b', '#2AD62A']}]);
        // create a Scale Bar
        var scaleBar = gauge.scaleBar(0);
        // set the height and offset of the Scale Bar (both as percentages of the gauge height)
        scaleBar.width('30%');
        scaleBar.offset('63.9%');
        // use the color scale (defined earlier) as the color scale of the Scale Bar
        scaleBar.colorScale(scaleBarColorScale);
        // add a marker pointer
        var marker = gauge.marker(0);
        // set the offset of the pointer as a percentage of the gauge width
        marker.offset('87%');
        // set the marker type
        marker.type('triangle-up');
        // set the zIndex of the marker
        marker.zIndex(10);
        marker.width(30);
        // configure the scale
        var scale = gauge.scale();
        scale.minimum(-10);
        scale.maximum(100);
        scale.ticks().interval(10);
        // configure the axis
        var axis = gauge.axis();
        axis.stroke('black');
        axis.minorTicks(true);
        axis.ticks().length(20);
        axis.ticks().stroke('black');
        axis.minorTicks().stroke('black');
        axis.width('2%');
        axis.offset('90%');
        axis.orientation('top');
        // format axis labels
        var valeurs=['vide','0%','10%','20%','30%','40%','50%','60%','70%','80%','90%','100%'];
        axis.labels().format(function() {
            var val = this.value;
            var index = (val + 10) / 10;  // car valeurs de -10 à 100 avec intervalle 10
            return valeurs[index] || '';  // retourne une chaîne vide si index invalide
        });
        axis.labels().fontColor('black');
        gauge.padding([0, 50]);
        gauge.container('jauge');
        gauge.draw();
        document.getElementsByClassName('anychart-credits')[0].innerHTML="";
    }
}

function couleur_region(dict){
    const etat2 = document.getElementById("clr").checked;
    if (etat2){
    $(".regions").css('fill','#d5d5da'); 
    $('.departements').css('fill','transparent');
    for (let element in dict){
        if (element=="Guadeloupe"){
            $('.Gua').css('fill', dict[element]);
        }
        $('#'+element).css('fill', dict[element]);
    }
    }else{
        $(".regions").css('fill',''); 
        $('.departements').css('fill','');
    }
}

//quand le document est chargé : 
$(document).ready(function () {
    document.getElementById('annee').value='2019';
    const $carte = $('#carte');
    $('#depts').css('pointer-events', 'none'); //impossible d'interagir avec les depts pour l'instant
    $('.Gua').on('mouseover', function () {
        const etat = document.getElementById("toggle").checked;
        if (etat) {
        var x=couleurs['color_nuit'];
        }else{
        var x=couleurs['color_reg_mouseover'];
        }
        $('.Gua').css('fill', x);
    });

    $('.Gua').on('mouseout', function () {
        $('.Gua').css('fill', ''); // remet la couleur par défaut du SVG
    });
    $('#regs .regions').click(function (e) {   /*lorsqu'une zone de la carte de la France a été cliqué*/
        e.stopPropagation();
        $('.regions').css('fill', '');
        $(this).css('fill', couleurs['color_reg_clique'] ); //couleur de la région cliqué change
        region_clique = "#" + this.id;
        //id correspondant au "groupe" de départements cliqué (les depts de la région quoi)
        var depts='#Depts_'+this.id;
        deptss=$(depts).find('.departements'); //on récupère chaque département de l'id récupéré
        //application du css : zoom, ajout/enlève la possibilité de cliquer/mouseover sur certains endroits
        envoie(this.id,"");
    // Applique le zoom dans la prochaine frame
        $carte.css('transform-origin', TOrigin[this.id]);
        // Active le will-change juste avant le zoom (permet de notifier le navig qu'on veut zoomer : le nav se "prépare" -> latence diminué)
        $carte.css('will-change', 'transform');
        requestAnimationFrame(() => {
            $carte.css(style);      //style appliqué
        });
        // Supprime will-change après la transition pour éviter le flou
        setTimeout(() => {
            $carte.css('will-change', 'auto');
        }, 300); 

        $('#regs').css('pointer-events', 'none');
        $(deptss).css('pointer-events', 'auto');
        $(deptss).mouseover(function () {
        //le if pour l'instant est un bout de code inutile (prendre en compte que le else), à voir pour la suite avec la gestion des requêtes :)
            if (departement_clique != "") {
                $('.departements').not(departement_clique).css('fill', '');
                $(departement_clique).css('fill',couleurs['color_dept_clique']); 
            } else {
                $('.departements').css('fill', '');
            }
            $(this).css('fill', couleurs['color_dept_mouseover']); //couleur de dept ou la souris passe dessus
            });
            $(deptss).click(function(){
                $(deptss).css('fill', '');
                $(this).css('fill', couleurs['color_dept_clique']); //couleur de la région cliqué change
                departement_clique="#"+this.id;
                envoie(this.id,"");
            });
            });
        $('#reg_OutreMer .regions').click(function (e) {
            e.stopPropagation();
            $('.regions').css('fill', '');
            const origin = this.classList.contains('Gua') ? TOrigin["Guadeloupe_972"] : TOrigin[this.id];

            if (this.classList.contains('Gua')) {
                $('.Gua').css('fill', couleurs['color_reg_clique']);
                envoie("","gua");
                region_clique = "#Guadeloupe";
            } else {
                $(this).css('fill', couleurs['color_reg_clique']);
                region_clique = "#" + this.id;
            }
            $carte.css('transform-origin', origin);
            $carte.css('will-change', 'transform');
            requestAnimationFrame(() => {
                $carte.css(style);
            });
            setTimeout(() => {
                $carte.css('will-change', 'auto');
            }, 300);
            $('#regs').css('pointer-events', 'none');
        });
    });

    function dezooming() {
        //tout réinit à la normale (y'a peut être moyen de faire mieux...)
        $('#carte').css(dezoom);
        $('#regs').css('pointer-events', '');
        $('#depts').css('pointer-events', 'none');
        $('.regions').css('fill', '');
        $('.departements').css('fill', '');
        $(deptss).css('pointer-events', 'none');
        region_clique = "";
        departement_clique = "";
        document.getElementById('jauge').innerHTML="";
    }

function mode_sombre() {
            // Envoyer la demande au serveur
            fetch('/toggle_theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                // Recharger la page pour appliquer le nouveau thème
                window.location.reload();
            });
        }
let barChart = null;
let barChart2 = null;
let lineChart = null;

function avant(){
    fetch('/static/graph_data_region.json')
        .then(resp => resp.json())
        .then(data => {
        couleur_region(data.couleur_region);
    })}


function graphiques(labels1, values1,labels2,values2) {
    if (barChart) {
        barChart.destroy();
    }
    if (barChart2){
        barChart2.destroy();
    }
    if (lineChart){
        lineChart.destroy();
    };
    const barCanvas2 = document.getElementById("barCanvas2");
    var vp61=labels1.indexOf("VP.061_m³");
    var val_vp61=values1[vp61];
    if (val_vp61){
    labels1.splice(vp61,1);
    values1.splice(vp61,1);
    barChart2 = new Chart(barCanvas2, {
        type: "bar",
        data: {
            labels:["VP.061_m³"],
            datasets: [{
                label: "Valeur de l'indicateur VP.061_m³",
                data: [val_vp61],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    })
    }
    const barCanvas = document.getElementById("barCanvas");
    const lineCanvas = document.getElementById("lineCanvas");
    barChart = new Chart(barCanvas, {
        type: "bar",
        data: {
            labels: labels1,
            datasets: [{
                label: "Valeur de l'indicateur",
                data: values1,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
    if (labels2!="rien"){
        lineChart = new Chart(lineCanvas, {
        type: "line",
        data: {
            labels: labels2,
            datasets: [{
                label: "Evolution par année whatever",
                data: values2,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
}
