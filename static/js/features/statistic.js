//  Подгонка ширины графика
// делал grok, я не буду в этом разбираться

// Ресайзим все графики Plotly при открытии вкладки "Графики"
document.addEventListener('DOMContentLoaded', function () {
    const graphsTab = document.getElementById('graphs-tab');

    graphsTab.addEventListener('shown.bs.tab', function () {
        // Небольшая задержка, чтобы DOM успел перестроиться
        setTimeout(function () {
            // Перебираем все графики на странице и делаем resize
            const graphs = document.querySelectorAll('#graphs .plotly-graph-div');
            graphs.forEach(div => {
                if (window.Plotly && div.id) {
                    try {
                        Plotly.Plots.resize(div);
                        // Или полная перерисовка (на всякий случай):
                        // Plotly.relayout(div, {});
                    } catch (e) {
                        console.log('Plotly resize skipped for', div.id);
                    }
                }
            });
        }, 100);
    });

    // Опционально: ресайз при изменении размера окна
    window.addEventListener('resize', function () {
        if (document.querySelector('#graphs.tab-pane.active')) {
            setTimeout(() => {
                document.querySelectorAll('#graphs .plotly-graph-div').forEach(div => {
                    if (window.Plotly && div.id) {
                        Plotly.Plots.resize(div);
                    }
                });
            }, 100);
        }
    });
});