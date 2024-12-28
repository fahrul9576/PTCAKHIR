// Inisialisasi Firebase setelah DOM dimuat
document.addEventListener('DOMContentLoaded', function () {
  const statusEl = document.getElementById('status');
  const tempSensorEl = document.getElementById('temp-sensor');
  const smokeSensorEl = document.getElementById('smoke-sensor');
  const historyTable = document.getElementById('history-table');

  try {
    let app = firebase.app();
    let database = firebase.database();

    statusEl.textContent = 'Terhubung ke Firebase';

    // Fungsi untuk mendapatkan referensi root
    function getRootReference() {
      return database.ref('DATA_SENSOR');
    }

    // Referensi ke sensor di database
    const sensorsRef = getRootReference().child('sensors');
    const historyRef = getRootReference().child('history');

    // Mendengarkan data sensor secara real-time
    sensorsRef.on(
      'value',
      (snapshot) => {
        const data = snapshot.val();
        if (data) {
          tempSensorEl.textContent = data.temperature ||
          smokeSensorEl.textContent = data.smoke ||
        }
      },
      (error) => {
        console.error('Sensor Error:', error);
        statusEl.textContent = 'Kesalahan saat memuat data sensor.';
      }
    );

    // Memuat riwayat aktivitas
    historyRef.on('value', (snapshot) => {
      const data = snapshot.val();
      historyTable.innerHTML = `
        <tr>
          <th>Date</th>
          <th>Type</th>
          <th>Location</th>
          <th>Status</th>
        </tr>
      `; // Reset tabel

      if (data) {
        Object.values(data).forEach((item) => {
          const row = historyTable.insertRow(-1);
          row.innerHTML = `
            <td>${item.date || '-'}</td>
            <td>${item.type || '-'}</td>
            <td>${item.location || '-'}</td>
            <td>${item.status || '-'}</td>
          `;
        });
      }
    });

    // Fungsi untuk menambahkan riwayat baru ke Firebase
    window.addHistory = function (date, type, location, status) {
      const newHistoryRef = historyRef.push();
      newHistoryRef
        .set({
          date,
          type,
          location,
          status,
        })
        .then(() => {
          console.log('Riwayat berhasil ditambahkan!');
        })
        .catch((error) => {
          console.error('Kesalahan saat menambahkan riwayat:', error);
        });
    };
  } catch (e) {
    console.error('Firebase Initialization Error:', e);
    statusEl.textContent = 'Gagal menghubungkan ke Firebase. Lihat konsol untuk detail.';
  }
});

// Fungsi tambahan untuk mengontrol perangkat
function toggleDevice(device) {
  alert(device + ' diaktifkan/dinonaktifkan!');
  addHistory(new Date().toLocaleString(), device, 'Lokasi Default', 'Berhasil');
}  