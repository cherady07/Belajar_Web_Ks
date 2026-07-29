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
