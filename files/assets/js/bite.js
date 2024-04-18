const bite = document.getElementById('bite').value
const bitedate = formatDate(new Date(bite*1000));
const bitetext = ` - Your house has been locked until ${bitedate}`;
document.getElementById('changing-house').querySelector('[selected]').innerHTML += bitetext;
