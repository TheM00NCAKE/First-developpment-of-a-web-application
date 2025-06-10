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
//dict pour les couleurs de la carte
var couleurs={color_region:'#f5f5fe',color_departement:'#f5f5fe',color_reg_mouseover:'#b2d3fb',color_reg_clique:'#cbcbfa',color_dept_clique:'#4472c4',color_dept_mouseover:'#94baff'};

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
function getannee(){
    return document.getElementById('annee').value;
}
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
var url="";
//fonction pour envoyer les données sur flask 
function envoie(zone_ou_search,id){
        document.getElementById('tableau_contenu').innerHTML=test;
        var annee_choisi=getannee()
        if (id=='gua'){
            url=`/Données_indicateurs?zone=Guadeloupe&annee=${encodeURIComponent(annee_choisi)}`;
        }else{
            url=`/Données_indicateurs?${encodeURIComponent(zone_ou_search)}=${encodeURIComponent(id)}&annee=${encodeURIComponent(annee_choisi)}`
        }
        fetch(url)
        .then(resp => resp.text())
        .then(html => {
            const parts = html.split("|");
            document.getElementById('tableau_contenu').innerHTML = parts[0];
            document.getElementById('jauge').innerHTML = parts[1];
            tri()
        });
    }

document.addEventListener('DOMContentLoaded', () => {
  tri();
});
/////////////////////////////Fin code tableau

//quand le document est chargé : 
$(document).ready(function () {
    document.getElementById('annee').value='2019';
    const $carte = $('#carte');
    $('#depts').css('pointer-events', 'none'); //impossible d'interagir avec les depts pour l'instant
    $('.Gua').on('mouseover', function () {
        $('.Gua').css('fill', couleurs['color_reg_mouseover']);
    });

    $('.Gua').on('mouseout', function () {
        $('.Gua').css('fill', ''); // remet la couleur par défaut du SVG
    });
    $('#regs .regions').click(function (e) {   /*lorsqu'une zone de la carte de la France a été cliqué*/
        e.stopPropagation();
        $('.regions').css('fill', '');
        $(this).css('fill', couleurs['color_reg_clique']); //couleur de la région cliqué change
        region_clique = "#" + this.id;
        //id correspondant au "groupe" de départements cliqué (les depts de la région quoi)
        var depts='#Depts_'+this.id;
        deptss=$(depts).find('.departements'); //on récupère chaque département de l'id récupéré
        //application du css : zoom, ajout/enlève la possibilité de cliquer/mouseover sur certains endroits
        envoie("zone",this.id);

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
                envoie("zone",this.id);
            });
            });
        $('#reg_OutreMer .regions').click(function (e) {
            e.stopPropagation();
            $('.regions').css('fill', '');
            const origin = this.classList.contains('Gua') ? TOrigin["Guadeloupe_972"] : TOrigin[this.id];

            if (this.classList.contains('Gua')) {
                $('.Gua').css('fill', couleurs['color_reg_clique']);
                envoie("zone","gua");
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
    }
    function chercher(){
    var motcle=document.getElementById('barre_filtrage').value;
    envoie("search",motcle);
    }

    function mode_sombre() {
    const styleClair = "/static/style.css";
    const styleSombre = "/static/style_sombre.css";

    const etat = document.getElementById("toggle").checked;
    const linkCSS = document.getElementById("theme");

    if (etat) {
        linkCSS.href = styleSombre;
    } else {
        linkCSS.href = styleClair;
    }
}
