document.addEventListener("DOMContentLoaded", function () {
    let forms = document.querySelectorAll(".edit-form");
    for (let f = 0; f < forms.length; f++) {
        forms[f].style.display = "none";
    }
    document.querySelectorAll(".edit").forEach((button) => {
        button.addEventListener("click", editButton);
    })
    document.querySelectorAll(".edit-btn").forEach((button) => {
        button.addEventListener("click", submitEdit);
    })
    document.querySelectorAll(".like").forEach((button) => {
        button.addEventListener("click", likeButton);
    })
    try {
        document.querySelector("#follow-btn").addEventListener("click", () => followUser());
    }
    catch { }
})

function editButton() {
    let buttonText = document.querySelector(`#${this.id}`).innerHTML;

    if (buttonText === "Edit") {
        document.querySelector(`#${this.id}`).innerHTML = "Cancel";
        document.querySelector(`#form-submit-${this.id}`).style.display = "block";
        document.querySelector(`#post-${this.id}`).style.display = "none";
    }
    else {
        document.querySelector(`#${this.id}`).innerHTML = "Edit";
        document.querySelector(`#form-submit-${this.id}`).style.display = "none";
        document.querySelector(`#post-${this.id}`).style.display = "block";
    }
}

function submitEdit() {
    let postString = this.id;
    var postNum = parseInt(postString.substring(12));
    var data = $(`#form-${this.id}`).serializeArray();
    submitFunction(data);

    function submitFunction(data) {
        $.ajax({
            type: "POST",
            url: `/edit/${postNum}`,
            dataType: "json",
            data: data,
            success: function (data) {
                document.querySelector(`#content-${postNum}`).value = data.content;
                document.querySelector(`#post-edit-${postNum}`).innerHTML = data.content;
                document.querySelector(`#post-edit-${postNum}`).style.display = "block";
                document.querySelector(`#form-submit-edit-${postNum}`).style.display = "none";
                document.querySelector(`#edit-${postNum}`).innerHTML = "Edit";
                
                let editTimestamp = document.querySelector(`#edited-timestamp-${postNum}`);
                let timeStamp = data.timestamp;
                const dateStamp = new Date(timeStamp);

                if (editTimestamp == null) {
                    const timestamp = document.createElement("p");
                    timestamp.innerHTML = `Edited ${data.timestamp}`;
                    document.querySelector(`#timestamp-div-${postNum}`).append(timestamp);
                    timestamp.style.fontSize = "small";
                }
                else {
                    editTimestamp.innerHTML = data.timestamp;
                    editTimestamp.style.fontSize = "small";
                }
            }
        });
    }
}

function likeButton() {
    var data = $(`#form-${this.id}`).serializeArray();
    var innerText = `likes-${this.id}`;
    var btn = this.id;
    likeFunction(data);
    
    function likeFunction(data) {
        $.ajax({
            type: "POST",
            url: `/like/${data[1].value}`,
            dataType: "json",
            data: data,
            success: function (data) {
                document.querySelector(`#${innerText}`).innerHTML = data.result
                let button = document.querySelector(`#${btn}`);
                if (button.innerHTML == "Like") {
                    button.innerHTML = "Unlike"
                }
                else {
                    button.innerHTML = "Like"
                }
            }
        });
        return false;
    }
}

function followUser() {
    var data = $("#form-follow").serializeArray();
    var buttonText = document.querySelector("#follow-btn");
    followFunction(data);

    function followFunction(data) {
        $.ajax({
            type: "POST",
            url: `/follow/${data[1].value}`,
            dataType: "json",
            data: data,
            success: function (data) {
                if (data.result === "removed") {
                    buttonText.innerHTML = "Follow";
                }
                else {
                    buttonText.innerHTML = "Unfollow";
                }
            }
        });
        return false;
    }
}
