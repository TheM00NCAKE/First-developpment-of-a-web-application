/*///////////////////////////
CE CODE EST UN PEU DEGUEU JE SAIS, JE COMPTE LE FINIR D'ABORD 
ET APRES L'OPTIMISER. SI VOUS AVEZ DES QUESTIONS, N'HESITEZ PAS A 
DEMANDER. -- . .-. -.-. .. (-.-. / - / .. ... .- -... . .-.. .-.. .)
*/
var region_clique = "";
var departement_clique = ""; //sert à rien pour l'instant
//style css permettant de faire un zoom
var style = {
    transform: 'scale(2.5)',
    transition: 'transform 0.3s ease-in',
};
        //dict contenant les coordonnées du point d'origine du zoom de chaque région 
        var TOrigin = { HautsDeFrance: '580px 0px', Normandie: '430px 50px', Bretagne: '210px 130px', GrandEst: '660px 100px', NouvelleAquitaine: '400px 420px', Occitanie: '500px 590px', IleDeFrance: '560px 100px', CentreValdeLoire: '500px 220px', PaysDeLaLoire: '360px 200px', BourgogneFrancheComté: '660px 200px', AuvergneRhôneAlpes: '660px 400px', ProvenceAlpesCôteDazur: '690px 500px', Corse: '900px 600px',Guyane_973:'0px 0px',Mayotte_976:'0px 90px',LaReunion_974:'0px 310px',Martinique_972:'0px 470px'}; //x y
        var dezoom = {
            transform: 'scale(1)',
            transition: 'transform 0.5 ease-out',
        };
        //couleurs de la carte
        var color_region='#f5f5fe';
        var color_departement='#f5f5fe';
        var color_reg_mouseover='#b2d3fb';
        var color_reg_clique='#cbcbfa';
        var color_dept_mouseover='#4472c4';
        //quand le document est chargé : 
        $(document).ready(function () {
            $(".regions").css('fill',color_region); //couleur region de base
            $(".departements").css('fill', color_departement); //couleur de département (les depts sont superposés sur les régions)
            $('#depts').css('pointer-events', 'none');
            $('.regions').mouseover(function () {
                if (region_clique != "") {
                    $('.regions').not(region_clique).css('fill', color_region); //les régions pas cliqués même couleur
                    $(region_clique).css('fill', color_reg_mouseover); //couleur de la région mouseover
                } else {
                    $('.regions').css('fill', color_region); //les régions pas cliqués même couleur
                } $(this).css('fill', color_reg_mouseover); //couleur quand la souris passe sur une région
            });
            $('.regions').click(function (e) {   /*lorsqu'une zone de la carte a été cliqué*/
                e.preventDefault();            /* annuler l'effet "habituelle" de l'évenement (quand on clique sur une zone, normalement celà amène l'utilisateur tout en haut de page, on ne veut pas ça)*/
                $('.regions').css('fill', color_region); //les régions pas cliqués même couleur
                $(this).css('fill', color_reg_clique); //couleur de la région cliqué
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
                    if (departement_clique != "") {
                        $('.departements').not(departement_clique).css('fill', color_departement); //couleur de dept reste la même (pas cliqué)
                        $(departement_clique).css('fill',color_dept_mouseover ); //couleur de dept ou la souris passe dessus
                    } else {
                        $('.departements').css('fill', color_departement); //rien de spécial 
                    }
                    $(this).css('fill', color_dept_mouseover); //couleur de dept ou la souris passe dessus
                });
            });
        });
        function dezooming() {
            //tout réinit à la normale (y'a peut être moyen de faire mieux...)
            $('#carte').css(dezoom);
            $('#regs').css('pointer-events', '');
            $('#depts').css('pointer-events', 'none');
            $('.regions').css('fill', color_region);  //reinit couleurs de base
            $('.departements').css('fill', color_departement);
            region_clique = "";
            $(deptss).css('pointer-events', 'none');
        }