document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const loadingModalElement = document.getElementById("loadingModal");
  const loadingModal = new bootstrap.Modal(loadingModalElement); // Instância única do modal
  const stopButton = document.getElementById("stopButton");
  const latitudeInput = document.getElementById("latitude");
  const longitudeInput = document.getElementById("longitude");
  const enderecoP = document.getElementById("endereco");
  const coordenadasP = document.getElementById("coordenadas");
  const editarBtn = document.getElementById("editarLocal");
  const mapModal = new bootstrap.Modal(document.getElementById("mapModal"));
  let isModalVisible = false;

  // Função para atualizar o endereço com base nas coordenadas
  function atualizarEndereco(lat, lon) {
    fetch(
      `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`
    )
      .then((res) => res.json())
      .then((data) => {
        const cidade =
          data.address.city ||
          data.address.town ||
          data.address.village ||
          "Localização desconhecida";
        const estado = data.address.state || "";
        enderecoP.textContent = `${cidade} - ${estado}`;
        coordenadasP.textContent = `Latitude: ${lat.toFixed(
          6
        )}, Longitude: ${lon.toFixed(6)}`;
      });
  }

  // Função para preencher os campos de localização
  function preencherLocalizacao(lat, lon) {
    latitudeInput.value = lat.toFixed(6);
    longitudeInput.value = lon.toFixed(6);
    atualizarEndereco(lat, lon);
  }

  // Localização automática ao carregar a página
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        preencherLocalizacao(lat, lon);
      },
      () => {
        enderecoP.textContent = "Erro ao detectar localização.";
      }
    );
  } else {
    enderecoP.textContent = "Seu navegador não suporta geolocalização.";
  }

  // Abertura do mapa para edição de localização
  editarBtn.addEventListener("click", () => {
    latitudeInput.removeAttribute("readonly");
    longitudeInput.removeAttribute("readonly");
    mapModal.show();

    setTimeout(() => {
      const lat = parseFloat(latitudeInput.value) || -10;
      const lon = parseFloat(longitudeInput.value) || -50;
      const map = L.map("map").setView([lat, lon], 6);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
      }).addTo(map);

      const marker = L.marker([lat, lon], { draggable: true }).addTo(map);

      map.on("click", (e) => {
        marker.setLatLng(e.latlng);
        preencherLocalizacao(e.latlng.lat, e.latlng.lng);
      });

      marker.on("dragend", () => {
        const pos = marker.getLatLng();
        preencherLocalizacao(pos.lat, pos.lng);
      });
    }, 500); // Delay para garantir que o modal carregue
  });

  let statusInterval = null;
  let currentThreadId = null;

  document.querySelector("form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    isModalVisible = true;
    loadingModal.show();

    // Inicia carregamento no servidor
    fetch("/iniciar-carregamento", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        const threadId = data.thread_id;
        buscarLogs(threadId); // Inicia polling
    });
});

function buscarLogs(threadId) {
    const logContainer = document.getElementById("logStatus");

    fetch(`/status?thread_id=${threadId}`)
        .then(res => res.json())
        .then(data => {
            const logs = data.logs || [];
            logContainer.textContent = logs[logs.length - 1] || "Iniciando..."; // Exibe apenas o último log

            if (!logs.some(log => log.includes("Processamento completo"))) {
                setTimeout(() => buscarLogs(threadId), 2000);
            } else {
                window.location.href = `/resultados?thread_id=${threadId}`;
            }
        })
        .catch(err => {
            console.error("Erro ao buscar logs:", err);
            logContainer.textContent = "[Erro ao buscar logs]";
        });
}

  // Adiciona o aviso ao tentar sair da página apenas se o modal de carregamento estiver ativo
  window.addEventListener("beforeunload", function (event) {
    if (isModalVisible) {
      // Exibe o aviso apenas se o modal estiver ativo
      event.preventDefault();
      event.returnValue =
        "Você tem certeza? Todo o progresso atual será perdido.";
    }
  });

  // Envia a solicitação para parar o carregamento apenas se o usuário realmente sair
  window.addEventListener("unload", function () {
    if (isModalVisible) {
      navigator.sendBeacon("/parar-carregamento"); // Usa sendBeacon para garantir que a solicitação seja enviada
    }
  });

  stopButton.addEventListener("click", function () {
    fetch("/parar-carregamento", {
      method: "POST",
    })
      .then((response) => response.json())
      .then(() => {
        clearInterval(statusInterval); // PARA o polling
        loadingModal.hide(); // Fecha o modal de carregamento
        isModalVisible = false;
      })
      .catch((error) => {
        console.error("Erro ao parar o carregamento:", error);
      });
  });
});
