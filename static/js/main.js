document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    form.addEventListener("submit", function(e){
        const password = form.querySelector("input[name='password']").value;
        if(password.length < 6){
            alert("Password must be at least 6 characters");
            e.preventDefault();
        }
    });
});
