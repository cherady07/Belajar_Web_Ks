const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
      }
    });
  },
  { threshold: 0.3 },
);

document.querySelectorAll(".fade-in").forEach((el) => observer.observe(el));

function tutupModal() {
  const modal = document.getElementById("modalSukses");
  if (modal) {
    modal.style.display = "none";
  }
  // hapus '?sukses=1&nama=...' dari URL tanpa reload halaman,
  // biar kalau customer refresh, modal nggak muncul lagi berulang
  window.history.replaceState({}, document.title, "/");
}

function tampilkanNamaFile(input) {
  const namaFileElement = document.getElementById("namaFileTerpilih");
  if (input.files.length > 0) {
    namaFileElement.textContent = "📎 File dipilih: " + input.files[0].name;
  } else {
    namaFileElement.textContent = "";
  }
}

function updateCountdown() {
  const elemenCountdown = document.querySelectorAll(".countdown");

  elemenCountdown.forEach((el) => {
    const selesai = new Date(el.dataset.selesai.replace(" ", "T"));
    const sekarang = new Date();
    const selisih = selesai - sekarang;

    if (selisih <= 0) {
      el.textContent = "Diskon berakhir";
      return;
    }

    const totalJam = Math.floor(selisih / (1000 * 60 * 60));

    if (totalJam >= 24) {
      // Lebih dari 24 jam: tampilkan dalam hari
      const hari = Math.floor(totalJam / 24);
      el.textContent = `⏰ Berakhir dalam ${hari} hari lagi`;
    } else {
      // Kurang dari 24 jam: tampilkan jam, menit, detik seperti biasa
      const jam = totalJam;
      const menit = Math.floor((selisih % (1000 * 60 * 60)) / (1000 * 60));
      const detik = Math.floor((selisih % (1000 * 60)) / 1000);
      el.textContent = `⏰ Berakhir dalam ${jam}j ${menit}m ${detik}d`;
    }
  });
}

updateCountdown();
setInterval(updateCountdown, 1000);
