// Получаем данные их файла
async function GetFilFromText(url_src) {
    const response = await fetch(url_src, {
        method: "GET",
    });
    return response.text();
}
local_url = 'http://localhost:8000/';
// Создать панель управления
async function CreateUI() {
    body_div = document.querySelector('html')
    elm = document.createElement('div')
    elm.innerHTML = await GetFilFromText(local_url + 'index.html')
    // console.log(elm);
    body_div.prepend(elm)
}
await CreateUI()
// Получаем данные их файла
async function GetFilFromJson(url_src) {
    const response = await fetch(url_src, {
        method: "GET",
    });
    return response.json();
}
// Текущии индекс выбранного пользователя 
select_index = 0
// Скачиваем файл
file_necessary_users = await GetFilFromJson(local_url + 'necessary_users.json');
// Следующий пользователь
NextUser = () => {
    select_index += 1
    ViewUser()
}
// Предыдущий пользователь
PreviousUser = () => {
    select_index -= 1
    ViewUser()
}
// Показать выбранного пользователя
ViewUser = () => {
    let user_id = file_necessary_users[select_index].user_id
    window.location.href = `https://vk.com/id${user_id}`;
}

