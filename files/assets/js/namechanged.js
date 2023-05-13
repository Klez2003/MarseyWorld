const namechanged = document.getElementById('namechanged').value
const namedate = formatDate(new Date(namechanged*1000));
const nametext = ` - Your username has been locked until ${namedate}`;
document.getElementById('name-body').value += nametext;
