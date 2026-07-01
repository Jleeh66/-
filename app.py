from flask import Flask, request, render_template_string
import math
import io
import base64

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


app = Flask(__name__)

G = 9.80665


HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>프로펠러 RPM 효율 최적화 계산기</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }

        .wrap {
            max-width: 1200px;
            margin: auto;
        }

        h1 {
            text-align: center;
            color: white;
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.1);
            letter-spacing: -0.5px;
        }

        h1::after {
            content: '';
            display: block;
            width: 100px;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            margin: 15px auto 40px;
            border-radius: 2px;
        }

        h2 {
            color: #333;
            font-size: 1.5em;
            margin-bottom: 20px;
            font-weight: 600;
        }

        .card {
            background: white;
            padding: 35px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 70px rgba(0,0,0,0.2);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
        }

        label {
            display: block;
            margin-top: 15px;
            font-weight: 600;
            font-size: 13px;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input {
            width: 100%;
            padding: 12px 15px;
            margin-top: 8px;
            border: 2px solid #e0e7ff;
            border-radius: 10px;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.3s ease;
            background: #f8f9ff;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        input::placeholder {
            color: #999;
        }

        button {
            margin-top: 30px;
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        }

        button:active {
            transform: translateY(0);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 13px;
        }

        th {
            background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
            color: #333;
            padding: 15px 10px;
            text-align: right;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #dfe7ff;
        }

        th:first-child {
            text-align: center;
        }

        td {
            padding: 12px 10px;
            border-bottom: 1px solid #f0f0f0;
            text-align: right;
        }

        td:first-child {
            text-align: center;
            font-weight: 500;
        }

        tr:hover {
            background: #f9faff;
        }

        .best {
            background: linear-gradient(135deg, #d4fc79 0%, #96f756 100%) !important;
            font-weight: 700;
            color: #2d5e1f;
        }

        .best:hover {
            background: linear-gradient(135deg, #c9f87f 0%, #8ee74a 100%) !important;
        }

        .result-box {
            background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
            border-left: 5px solid #667eea;
            padding: 25px;
            line-height: 2;
            margin-top: 20px;
            border-radius: 12px;
            font-size: 15px;
            color: #333;
        }

        .result-box b {
            color: #667eea;
            font-weight: 600;
        }

        .error {
            background: linear-gradient(135deg, #ffe6e6 0%, #ffd4d4 100%);
            color: #8b0000;
            border: 2px solid #ff6b6b;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-weight: 500;
        }

        img {
            max-width: 100%;
            margin-top: 25px;
            border: 1px solid #e0e7ff;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .note {
            font-size: 13px;
            color: #666;
            line-height: 1.8;
            margin-top: 25px;
            padding: 20px;
            background: #f9faff;
            border-left: 4px solid #667eea;
            border-radius: 8px;
        }

        .note p {
            margin: 10px 0;
        }

        .note b {
            color: #667eea;
            font-weight: 600;
        }

        @media (max-width: 900px) {
            .grid {
                grid-template-columns: 1fr;
            }

            h1 {
                font-size: 2em;
            }

            .card {
                padding: 25px;
            }
        }
    </style>
</head>
<body>
<div class="wrap">
    <h1>프로펠러 RPM 효율 최적화 계산기</h1>

    {% if error %}
    <div class="error">
        {{ error }}
    </div>
    {% endif %}

    <div class="card">
        <h2>입력값</h2>

        <form method="POST">
            <div class="grid">
                <div>
                    <label>프로펠러 직경 D [m]</label>
                    <input type="number" step="any" name="D" value="{{ values.D }}" required>

                    <label>유입속도 Va [m/s]</label>
                    <input type="number" step="any" name="Va" value="{{ values.Va }}" required>

                    <label>물의 밀도 ρ [kg/m³]</label>
                    <input type="number" step="any" name="rho" value="{{ values.rho }}" required>
                </div>

                <div>
                    <label>최소 RPM</label>
                    <input type="number" step="any" name="rpm_min" value="{{ values.rpm_min }}" required>

                    <label>최대 RPM</label>
                    <input type="number" step="any" name="rpm_max" value="{{ values.rpm_max }}" required>

                    <label>RPM 간격</label>
                    <input type="number" step="any" name="rpm_step" value="{{ values.rpm_step }}" required>
                </div>

                <div>
                    <label>요구 추력 T_required [N]</label>
                    <input type="number" step="any" name="T_required" value="{{ values.T_required }}">

                    <label>Kt0</label>
                    <input type="number" step="any" name="Kt0" value="{{ values.Kt0 }}" required>

                    <label>Kt1</label>
                    <input type="number" step="any" name="Kt1" value="{{ values.Kt1 }}" required>

                    <label>Kq0</label>
                    <input type="number" step="any" name="Kq0" value="{{ values.Kq0 }}" required>

                    <label>Kq1</label>
                    <input type="number" step="any" name="Kq1" value="{{ values.Kq1 }}" required>
                </div>
            </div>

            <button type="submit">최적 RPM 계산하기</button>
        </form>

        <div class="note">
            <p>
                이 계산기는 간단화를 위해 Kt, Kq를 다음 선형 모델로 계산합니다.
            </p>
            <p>
                <b>Kt = Kt0 - Kt1 × J</b><br>
                <b>Kq = Kq0 - Kq1 × J</b>
            </p>
            <p>
                실제 설계에서는 Wageningen B-Series, 모형시험, CFD, Open-water test 데이터 등을 사용해야 합니다.
            </p>
        </div>
    </div>

    {% if best %}
    <div class="card">
        <h2>최적 RPM 결과</h2>

        <div class="result-box">
            <b>최적 RPM:</b> {{ best.rpm }} rpm<br>
            <b>최대 단독효율 η₀:</b> {{ best.eta }}<br>
            <b>전진비 J:</b> {{ best.J }}<br>
            <b>추력 T:</b> {{ best.T }} N<br>
            <b>토크 Q:</b> {{ best.Q }} N·m<br>
            <b>전달동력 PD:</b> {{ best.PD }} kW
        </div>

        {% if chart %}
        <img src="data:image/png;base64,{{ chart }}" alt="RPM 효율 그래프">
        {% endif %}
    </div>
    {% endif %}

    {% if results %}
    <div class="card">
        <h2>RPM별 계산 결과</h2>

        <table>
            <tr>
                <th>RPM</th>
                <th>n [rps]</th>
                <th>J</th>
                <th>Kt</th>
                <th>Kq</th>
                <th>T [N]</th>
                <th>Q [N·m]</th>
                <th>PD [kW]</th>
                <th>η₀</th>
            </tr>

            {% for r in results %}
            <tr class="{% if best and r.rpm == best.rpm %}best{% endif %}">
                <td>{{ r.rpm }}</td>
                <td>{{ r.n }}</td>
                <td>{{ r.J }}</td>
                <td>{{ r.Kt }}</td>
                <td>{{ r.Kq }}</td>
                <td>{{ r.T }}</td>
                <td>{{ r.Q }}</td>
                <td>{{ r.PD }}</td>
                <td>{{ r.eta }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}
</div>
</body>
</html>
"""


def to_float(name, default=None):
    value = request.form.get(name)

    if value is None or value.strip() == "":
        if default is not None:
            return default
        raise ValueError(f"{name} 값이 비어 있습니다.")

    return float(value)


def positive(value, label):
    if value <= 0:
        raise ValueError(f"{label} 값은 0보다 커야 합니다.")


def fmt(value, digits=4):
    return f"{value:,.{digits}f}"


def calculate_propeller_rpm_optimization(
    D,
    Va,
    rho,
    rpm_min,
    rpm_max,
    rpm_step,
    T_required,
    Kt0,
    Kt1,
    Kq0,
    Kq1
):
    results = []

    rpm = rpm_min

    while rpm <= rpm_max + 1e-9:
        n = rpm / 60.0

        if n <= 0:
            rpm += rpm_step
            continue

        J = Va / (n * D)

        Kt = Kt0 - Kt1 * J
        Kq = Kq0 - Kq1 * J

        if Kt <= 0 or Kq <= 0:
            rpm += rpm_step
            continue

        T = rho * (n ** 2) * (D ** 4) * Kt
        Q = rho * (n ** 2) * (D ** 5) * Kq
        PD = 2 * math.pi * n * Q / 1000.0

        eta = (J * Kt) / (2 * math.pi * Kq)

        if eta <= 0:
            rpm += rpm_step
            continue

        # 단순 모델에서는 비현실적으로 효율이 1을 넘을 수 있어 제한
        if eta > 1.0:
            rpm += rpm_step
            continue

        row = {
            "rpm_raw": rpm,
            "rpm": round(rpm, 2),
            "n": fmt(n),
            "J_raw": J,
            "J": fmt(J),
            "Kt_raw": Kt,
            "Kt": fmt(Kt),
            "Kq_raw": Kq,
            "Kq": fmt(Kq),
            "T_raw": T,
            "T": fmt(T, 2),
            "Q_raw": Q,
            "Q": fmt(Q, 2),
            "PD_raw": PD,
            "PD": fmt(PD, 2),
            "eta_raw": eta,
            "eta": fmt(eta)
        }

        results.append(row)

        rpm += rpm_step

    if not results:
        return [], None

    feasible_results = results

    if T_required is not None and T_required > 0:
        feasible_results = [
            r for r in results
            if r["T_raw"] >= T_required
        ]

    if not feasible_results:
        return results, None

    best = max(feasible_results, key=lambda r: r["eta_raw"])

    return results, best


def make_chart(results, best):
    rpms = [r["rpm_raw"] for r in results]
    etas = [r["eta_raw"] for r in results]
    thrusts = [r["T_raw"] for r in results]

    fig, ax1 = plt.subplots(figsize=(9, 5))

    ax1.plot(rpms, etas, marker="o", label="Efficiency η₀")
    ax1.set_xlabel("RPM")
    ax1.set_ylabel("Efficiency η₀")
    ax1.grid(True)

    if best:
        ax1.scatter(
            [best["rpm_raw"]],
            [best["eta_raw"]],
            s=100,
            label="Best RPM"
        )

    ax2 = ax1.twinx()
    ax2.plot(rpms, thrusts, marker="x", linestyle="--", label="Thrust T")
    ax2.set_ylabel("Thrust [N]")

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="best")

    plt.title("Propeller RPM Optimization")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=150)
    plt.close(fig)

    img.seek(0)
    chart_base64 = base64.b64encode(img.read()).decode("utf-8")

    return chart_base64


@app.route("/", methods=["GET", "POST"])
def index():
    values = {
        "D": 2.5,
        "Va": 6.0,
        "rho": 1025,
        "rpm_min": 80,
        "rpm_max": 300,
        "rpm_step": 10,
        "T_required": 20000,
        "Kt0": 0.45,
        "Kt1": 0.30,
        "Kq0": 0.065,
        "Kq1": 0.030
    }

    results = []
    best = None
    chart = None
    error = None

    if request.method == "POST":
        try:
            D = to_float("D")
            Va = to_float("Va")
            rho = to_float("rho")
            rpm_min = to_float("rpm_min")
            rpm_max = to_float("rpm_max")
            rpm_step = to_float("rpm_step")
            T_required = to_float("T_required", default=0)

            Kt0 = to_float("Kt0")
            Kt1 = to_float("Kt1")
            Kq0 = to_float("Kq0")
            Kq1 = to_float("Kq1")

            positive(D, "프로펠러 직경 D")
            positive(Va, "유입속도 Va")
            positive(rho, "물의 밀도 ρ")
            positive(rpm_min, "최소 RPM")
            positive(rpm_max, "최대 RPM")
            positive(rpm_step, "RPM 간격")

            if rpm_min >= rpm_max:
                raise ValueError("최소 RPM은 최대 RPM보다 작아야 합니다.")

            if rpm_step > (rpm_max - rpm_min):
                raise ValueError("RPM 간격이 너무 큽니다.")

            values = {
                "D": D,
                "Va": Va,
                "rho": rho,
                "rpm_min": rpm_min,
                "rpm_max": rpm_max,
                "rpm_step": rpm_step,
                "T_required": T_required,
                "Kt0": Kt0,
                "Kt1": Kt1,
                "Kq0": Kq0,
                "Kq1": Kq1
            }

            results, best = calculate_propeller_rpm_optimization(
                D=D,
                Va=Va,
                rho=rho,
                rpm_min=rpm_min,
                rpm_max=rpm_max,
                rpm_step=rpm_step,
                T_required=T_required,
                Kt0=Kt0,
                Kt1=Kt1,
                Kq0=Kq0,
                Kq1=Kq1
            )

            if not results:
                raise ValueError("계산 가능한 RPM 구간이 없습니다. Kt, Kq 계수나 RPM 범위를 조정하세요.")

            if best is None:
                error = "요구 추력을 만족하는 RPM이 없습니다. 요구 추력을 낮추거나 RPM 범위를 높이세요."
            else:
                chart = make_chart(results, best)

        except ValueError as e:
            error = f"입력 오류: {e}"
        except Exception as e:
            error = f"계산 중 오류 발생: {e}"

    return render_template_string(
        HTML,
        values=values,
        results=results,
        best=best,
        chart=chart,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
