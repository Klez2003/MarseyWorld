const post_permalinks = document.getElementById('post_permalinks').value.slice(1, -1)
sessionStorage.setItem("post_permalinks", post_permalinks);

const next_page_url = document.getElementById('next_page_url').value
sessionStorage.setItem("next_page_url", next_page_url);
