// Tailwind CSS — saytın istifadə etdiyi class-lar build zamanı assets/tailwind.css-ə yığılır
// (əvvəl cdn.tailwindcss.com skripti hər ziyarətçinin brauzerində işləyirdi).
// python3 _dev/build.py avtomatik işlədir; yalnız npm install edilmiş _dev lazımdır.
module.exports = {
    content: {
        relative: true,
        files: ['../*.html', '../lessons/*.html', '../tools/*.html', '../assets/*.js', './lessons/*.html'],
    },
    theme: { extend: {} },
    plugins: [],
};
