/*///////////////////////////
CE CODE EST UN PEU DEGUEU JE SAIS, JE COMPTE LE FINIR D'ABORD 
ET APRES L'OPTIMISER. SI VOUS AVEZ DES QUESTIONS, N'HESITEZ PAS A 
DEMANDER. -- . .-. -.-. .. (-.-. / - / .. ... .- -... . .-.. .-.. .)

Petite parenthèse : la Guadeloupe est une région "spéciale" dans le code : 
Chaque région est défini par un seul polygone <path> dans un groupe <g (avec un id)>, mais la Guadeloupe est composé de plusieurs polygones 
différents. Le code était censé spécifique à un seul polygone pour chaque évènement, mais vu que j'y arrive pas MDR, il y a des lignes 
spécifiques pour la région de la Guadeloupe (identifié par ses polygones de classe régions ET 'Gua')*/
var region_clique = "";
var departement_clique = ""; //sert à rien pour l'instant
//style css permettant de faire un zoom
var style = {
    transform: 'scale(2.5)',
    transition: 'transform 0.3s ease-in',
};
//dict contenant les coordonnées du point d'origine du zoom de chaque région 
var TOrigin = { HautsDeFrance: '580px 0px', Normandie: '430px 50px', Bretagne: '210px 130px', GrandEst: '660px 100px', NouvelleAquitaine: '400px 420px', Occitanie: '500px 590px', IleDeFrance: '560px 100px', CentreValdeLoire: '500px 220px', PaysDeLaLoire: '360px 200px', BourgogneFrancheComté: '660px 200px', AuvergneRhôneAlpes: '660px 400px', ProvenceAlpesCôteDazur: '690px 500px', Corse: '900px 600px',Guyane_973:'0px 0px',Mayotte_976:'0px 90px',LaReunion_974:'0px 310px',Martinique_972:'0px 470px',Guadeloupe_972:'0px 600px'}; //x y
var dezoom = {
    transform: 'scale(1)',
    transition: 'transform 1 ease-out',
};
var deptss = $(); 
//dict pour les couleurs de la carte
var couleurs={color_region:'#f5f5fe',color_departement:'#f5f5fe',color_reg_mouseover:'#b2d3fb',color_reg_clique:'#cbcbfa',color_dept_mouseover:'#4472c4'};
//quand le document est chargé : 
$(document).ready(function () {
    $(".regions").css('fill',couleurs['color_region']); //couleur region de base
    $(".departements").css('fill', couleurs['color_departement']); //couleur de département (les depts sont superposés sur les régions)
    $('#depts').css('pointer-events', 'none'); //impossible d'interagir avec les depts pour l'instant
    $('.regions').mouseover(function (e) {         
        e.stopPropagation();  //parfois la gestion des évènements est bordélique, donc les function() exec plusieurs fois. Ca permet d'éviter ce problème
        if (this.classList.contains('Gua')){ 
            $('.regions').css('fill', couleurs['color_region']);
            $('.Gua').css('fill',couleurs['color_reg_mouseover']);
        } else {
            $('.regions').css('fill', couleurs['color_region']); //les régions pas cliqués ne changent pas de couleurs
            } $(this).css('fill', couleurs['color_reg_mouseover']); //couleur quand la souris passe sur une région
         });
    $('#regs .regions').click(function (e) {   /*lorsqu'une zone de la carte de la France a été cliqué*/
        e.stopPropagation();
        $('.regions').css('fill', couleurs['color_region']); 
        $(this).css('fill', couleurs['color_reg_clique']); //couleur de la région cliqué change
        region_clique = "#" + this.id;
        //id correspondant au "groupe" de départements cliqué (les depts de la région quoi)
        var depts='#Depts_'+this.id;
        deptss=$(depts).find('.departements'); //on récupère chaque département de l'id récupéré
        //application du css : zoom, ajout/enlève la possibilité de cliquer/mouseover sur certains endroits
        $('#carte').css(style);
        $('#carte').css('transform-origin', TOrigin[this.id]);
        $('#regs').css('pointer-events', 'none');
        $(deptss).css('pointer-events', 'auto');
        $(deptss).mouseover(function () {
        //le if pour l'instant est un bout de code inutile (prendre en compte que le else), à voir pour la suite avec la gestion des requêtes :)
        if (departement_clique != "") {
            $('.departements').not(departement_clique).css('fill', couleurs['color_departement']); 
            $(departement_clique).css('fill',couleurs['color_dept_mouseover']); 
        } else {
            $('.departements').css('fill', couleurs['color_departement']); //rien de spécial 
        }
        $(this).css('fill', couleurs['color_dept_mouseover']); //couleur de dept ou la souris passe dessus
        });
        });
        $('#reg_OutreMer .regions').click(function (e) {   /*lorsqu'une zone de la carte d'Outre Mer a été cliqué*/
            e.stopPropagation();
            $('.regions').css('fill', couleurs['color_region']); 
            if (this.classList.contains('Gua')){
                $('.Gua').css('fill',couleurs['color_reg_clique']);
                $('#carte').css(style);
                $('#carte').css('transform-origin', TOrigin["Guadeloupe_972"]);
            }else{
                $(this).css('fill', couleurs['color_reg_clique']); 
                //couleur de la région cliqué
                region_clique = "#" + this.id;
                $('#carte').css(style);
                $('#carte').css('transform-origin', TOrigin[this.id]);
            }
            $('#regs').css('pointer-events', 'none');
        });
    });
    function dezooming() {
        //tout réinit à la normale (y'a peut être moyen de faire mieux...)
        $('#carte').css(dezoom);
        $('#regs').css('pointer-events', '');
        $('#depts').css('pointer-events', 'none');
        $('.regions').css('fill', couleurs['color_region']);  //reinit couleurs de base
        $('.departements').css('fill', couleurs['color_departement']);
        $(deptss).css('pointer-events', 'none');
        region_clique = "";
    }