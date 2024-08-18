const marsified = document.getElementById('marsified').value
const marsified_date = formatTime(new Date(marsified*1000));
const marsified_text = `You're marsified until ${marsified_date}`;
document.getElementById('marsifyswitch').nextElementSibling.innerHTML += marsified_text;
