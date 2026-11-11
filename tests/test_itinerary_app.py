from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "src" / "app" / "main.py"


def test_itinerary_compares_complete_days_and_clears_old_results():
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
    app.radio[0].set_value("3. Itinerario Turístico (ATSP)").run()
    assert not app.exception

    # Las visitas suman 810 min; ningún recorrido cabe aunque los traslados sí.
    app.multiselect[0].set_value([16, 17, 18, 20, 21, 23, 26])
    app.button[0].click().run()
    assert not app.exception
    metrics = {metric.label: metric for metric in app.metric}
    assert metrics["Jornada con Held-Karp"].value == "970.1 min"
    assert metrics["Jornada con la heurística voraz"].value == "988.9 min"
    assert metrics["Diferencia de jornada (Voraz − Held-Karp)"].delta == "1.93%"
    assert "Ningún recorrido cabe en 11 h" in app.warning[0].value
    assert app.dataframe[0].value.iloc[-1]["Visita (min)"] == "-"

    # Un rerun sin cambiar la selección (por ejemplo, al mover el mapa) conserva el resultado.
    app.run()
    assert len(app.metric) == 3
    app.selectbox[0].set_value(2).run()
    assert not app.metric
    assert app.info

    app.selectbox[0].set_value(1)
    app.multiselect[0].set_value([16, 17, 20, 21, 25, 26])
    app.button[0].click().run()
    assert not app.exception
    assert [metric.value for metric in app.metric] == ["608.9 min", "618.6 min", "9.7 min"]
    assert "Ambos recorridos caben" in app.success[0].value

    app.multiselect[0].set_value([16, 17, 20, 21, 25])
    app.button[0].click().run()
    assert not app.exception
    assert "seleccionados: 5" in app.error[0].value
    assert not app.metric
