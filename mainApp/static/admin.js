function deleteUser(userid){
    fetch("/delete-user",{
        method:"POST",
        body:JSON.stringify({userid: userid}),
    }).then((_res) => {
        window.location.href = "/admin";
    })
}

function deleteLoan(loanid){
    fetch("/delete-loan",{
        method:"POST",
        body:JSON.stringify({loanid: loanid}),
    }).then((_res) => {
        window.location.href = "/admin";
    })
}
function deletePay(payid){
    fetch("/delete-pay",{
        method:"POST",
        body:JSON.stringify({payid: payid}),
    }).then((_res) => {
        window.location.href = "/admin";
    })
}

function approveSend(loanid){
    fetch("/send-loan",{
        method:"POST",
        body:JSON.stringify({loanid: loanid}),
    }).then((_res) => {
        window.location.href = "/admin";
    })
}