// Массив с картинками для смены
const images = [
    "https://pbs.twimg.com/profile_banners/176626779/1610495469/1500x500",
    "https://cstor.nn2.ru/blog/data/blog/2019-01/1859976_1548098983.jpg",
    "https://files.glotr.uz/site/000/021/593/banners/2021-04-13-10-07-14-033587-b11113e9942f234976b42fc6e1451bf9.jpeg?_=gza13",
    "https://avatars.mds.yandex.net/i?id=7c3ff7222ffba3386b353157011c5522_l-4898876-images-thumbs&n=13",
    "https://kolbehatr.com/Upload/Content/Content/cdaa5bc7-22ae-42d8-818d-3f867e1805d2.jpg",
    "https://media.allure.com/photos/57b32151256a10546425ad61/master/w_4961,h_3189,c_limit/LV%20PARFUMS_6-7.jpg",
    "https://yandex-images.clstorage.net/5BvmD1172/4d35d8GdP/prhqH9RR6x6w-286xE2heFzo6DNlW4sp3QXo-vfUSfCXctyDkL9CO5P_2dO6LZu1WvRwDr0qqOucUVpMT0BvJu-1Ky6VSJICsO8-Fu19yUgcvdhGaQ6DTc0YjMurPLA5Wp9oOhFf0pczi83m92Sf1XqMmZOk_jGSlTSTQB-VklvuvEqXtAWaFrBTBl7oKZUIDCHknzHqC5QpFe0-01Bw8Z7fmDrNE9YDT_Nlil9EFoXevGGu4PKpbgkAM3jXPYLH6sD-ixxNEh4oz_aifFWxtKwtmDPR6j_UYcFJVvOUiJXWI5w2YTdGr8MPQXI_wJY1MsDZ0hDKjfIJ0E8UCyn2N2JQJm_0Nf6GFON6qkABRTwE1Rg3lcJvPLGBsYqzxOhhWsfATgnvUvevJ5F61_RW6dJQxfZo8omqkUSrvFMV4pfy1C5_aKmu_kDXnk6Ubd20QA14D8kii9SZeT1WYxgIiU4fDN6RswYnJwdZPu_ESrGGrMW6gFoZbg2gH9CjeUpD7ixy-zTN6pqc36pSjAFVgHzdYG_ZkgtcySUhJiPMZHVmX9xCxVeq92870VJvMLK9wkw9BqxuSbYpGMvIc03SX67wotcEiZKCuDPyUqRxXWzsnYDT9ZIjGLX1XQKrXAzVEls0jm3D9itHJxGa8-ymPcIEdQa48mWC-TArjGvBwpc61GabQNlCGjjn9ob0eZHYrMFEu2kuuyT5BV3m_yAEZfon3M6Js2qXR8cJGgP4ynF2eK0mGHIxAsHAS6wTYfaz4sBKQwARbjZQr-IOKCG9YKhBWCfRoms8STF9qseMgA1-X1Qa8e_GixfLWQJ3aHblckh5yqweee7V5HMUG5num6oIJkMQvYJmzLPyVqh9sWD0lXTH6cqnxJmpEe5TjJiJlk_IKmVL8vOv91U206y2LUbcoWKgTqUuLaDXwLcpYs9-KFoXzLm6RqwLdma0KR14fF1IJ6neuzDJRSE-Jwik",
    
];

// Создаем элементы img для каждой картинки и добавляем их в слайдер
const sliderContainer = document.querySelector('.image-slider');
images.forEach((image, index) => {
    const imgElement = document.createElement('img');
    imgElement.src = image;
    if (index === 0) imgElement.classList.add('active'); // Первая картинка активна
    sliderContainer.appendChild(imgElement);
});

let currentIndex = 0;
const imgElements = document.querySelectorAll('.image-slider img');

// Функция для смены картинки
function changeImage() {
    // Убираем класс active с текущей картинки
    imgElements[currentIndex].classList.remove('active');

    // Увеличиваем индекс и сбрасываем, если дошли до конца
    currentIndex = (currentIndex + 1) % images.length;

    // Добавляем класс active к следующей картинке
    imgElements[currentIndex].classList.add('active');
}

// Меняем картинку
setInterval(changeImage, 1500);