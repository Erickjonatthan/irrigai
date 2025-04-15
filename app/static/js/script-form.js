document.addEventListener("DOMContentLoaded", () => {
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
  let cancelamentoSolicitado = false;

  const threadEmAndamento = localStorage.getItem("thread_id_em_andamento");
  if (threadEmAndamento) {
    isModalVisible = true;
    loadingModal.show();
    buscarLogs(threadEmAndamento); // Retoma o polling
  }

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

  let statusInterval = null; // Variável global para controlar o polling

  document.querySelector("form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    isModalVisible = true;
    loadingModal.show();

    // Inicia carregamento no servidor
    fetch("/iniciar-carregamento", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        cancelamentoSolicitado = false;
        const threadId = data.thread_id;

        // SALVA O THREAD_ID NO LOCALSTORAGE
        localStorage.setItem("thread_id_em_andamento", threadId);

        buscarLogs(threadId); // Inicia polling
      });
  });

  function buscarLogs(threadId) {
    const logContainer = document.getElementById("logStatus");
    const progressBar = document.getElementById("progressBar");

    fetch(`/status?thread_id=${threadId}`)
      .then((res) => res.json())
      .then((data) => {
        const logs = data.logs || [];
        let ultimoLog = logs[logs.length - 1] || "Iniciando...";

        const cancelado = logs.some(
          (log) =>
            log.includes("cancelada") ||
            log.includes("interrompido") ||
            log.includes("Processo interrompido pelo usuário") ||
            log.includes("Erro") ||
            log.includes("Cache limpo")
        );

        const completo = logs.some((log) =>
          log.includes("Processamento completo")
        );

        // Atualiza a barra de progresso
        const progresso = Math.min((logs.length / 20) * 100, 100); // Supondo 10 etapas
        progressBar.style.width = `${progresso}%`;
        progressBar.setAttribute("aria-valuenow", progresso);

        if (cancelamentoSolicitado) {
          const cancelamentoLogs = logs.filter(
            (log) =>
              log.includes("Cancelada") ||
              log.includes("Interrompido") ||
              log.includes("Processo interrompido pelo usuário") ||
              log.includes("Erro") ||
              log.includes("Cache limpo")
          );

          if (cancelamentoLogs.length > 0) {
            ultimoLog = cancelamentoLogs[cancelamentoLogs.length - 1];
            logContainer.textContent = ultimoLog;
          } else {
            logContainer.textContent = "Cancelando...";
          }

          if (cancelado) {
            clearTimeout(statusInterval);
            setTimeout(() => {
              loadingModal.hide();
              isModalVisible = false;
            }, 1500);
          } else {
            statusInterval = setTimeout(() => buscarLogs(threadId), 2000);
          }

          return;
        }

        logContainer.textContent = ultimoLog;

        if (completo || cancelado) {
          clearTimeout(statusInterval);
          localStorage.removeItem("thread_id_em_andamento");

          if (completo) {
            progressBar.style.width = "100%"; // Completa a barra
            window.location.href = `/resultados?thread_id=${threadId}`;
          } else {
            setTimeout(() => {
              loadingModal.hide();
              isModalVisible = false;
            }, 1500);
          }
          return;
        } else {
          statusInterval = setTimeout(() => buscarLogs(threadId), 2000);
        }
      })
      .catch((err) => {
        console.error("Erro ao buscar logs:", err);
        logContainer.textContent = "[Erro ao buscar logs]";
      });
  }

  stopButton.addEventListener("click", function () {
    const logContainer = document.getElementById("logStatus");
    logContainer.textContent = "Cancelando...";
    cancelamentoSolicitado = true;

    // REMOVE O THREAD_ID DO LOCALSTORAGE
    localStorage.removeItem("thread_id_em_andamento");

    fetch("/parar-carregamento", {
      method: "POST",
    })
      .then((response) => response.json())
      .catch((error) => {
        console.error("Erro ao parar o carregamento:", error);
        logContainer.textContent = "[Erro ao tentar cancelar]";
      });
  });
});
