const navbar =document.getElementById('navbar');
const menu =document.getElementById('menu');

menu.addEventListener('click', () =>{
    navbar.classList.toggle('display');
    menu.classList.toggle('menu');
});