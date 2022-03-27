const cardList = document.querySelectorAll('.card');

cardList.forEach(card => {
    card.addEventListener('click', function(e) {
        e.preventDefault();
        let id = this.getAttribute('id');
        console.log(id);
        let baseUrl = window.location.origin;
        window.location.replace(`${baseUrl}/view_service?id=${id}`);
    });
});