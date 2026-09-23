from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


# ============================================================
# Health
# ============================================================

def test_health_contract():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "service" in data


# ============================================================
# Cookie Cats experimentation
# ============================================================

def test_cookie_cats_experiment_contract():
    response = client.get("/api/analytics/experiment")

    assert response.status_code == 200

    data = response.json()

    required_top_level = {
        "summary",
        "retention",
        "tests",
        "rounds",
        "decision",
        "result_source",
    }

    assert required_top_level.issubset(data)

    assert data["result_source"] == "results/cookie_cats"

    assert isinstance(data["summary"], dict)
    assert isinstance(data["retention"], list)
    assert isinstance(data["tests"], list)
    assert isinstance(data["rounds"], dict)
    assert isinstance(data["decision"], list)

    assert len(data["retention"]) > 0

    retention_row = data["retention"][0]

    required_retention_fields = {
        "metric",
        "gate_30_rate",
        "gate_40_rate",
        "p_value",
    }

    assert required_retention_fields.issubset(
        retention_row
    )

    assert len(data["decision"]) > 0

    decision_row = data["decision"][0]

    assert "metric" in decision_row
    assert "action" in decision_row


# ============================================================
# Online Retail II
# ============================================================

def test_online_retail_contract():
    response = client.get(
        "/api/analytics/online-retail"
    )

    assert response.status_code == 200

    data = response.json()

    required_top_level = {
        "summary",
        "split_summary",
        "business_overview",
        "customer_summary",
        "top_countries",
        "result_source",
    }

    assert required_top_level.issubset(data)

    assert (
        data["result_source"]
        == "results/online_retail"
    )

    summary = data["summary"]

    required_summary_fields = {
        "clean_rows",
        "customers",
        "total_revenue",
        "date_start",
        "date_end",
    }

    assert required_summary_fields.issubset(
        summary
    )

    assert isinstance(data["split_summary"], list)
    assert len(data["split_summary"]) > 0

    split_row = data["split_summary"][0]

    assert {
        "split",
        "rows",
        "customers",
    }.issubset(split_row)


# ============================================================
# Retailrocket behavioral analytics
# ============================================================

def test_retailrocket_analytics_contract():
    response = client.get(
        "/api/analytics/retailrocket"
    )

    assert response.status_code == 200

    data = response.json()

    required_top_level = {
        "overview",
        "funnel",
        "engagement",
        "result_source",
    }

    assert required_top_level.issubset(data)

    assert (
        data["result_source"]
        == "results/retailrocket"
    )

    assert isinstance(data["overview"], list)
    assert isinstance(data["funnel"], list)
    assert isinstance(data["engagement"], list)

    assert len(data["overview"]) > 0
    assert len(data["funnel"]) > 0

    funnel_row = data["funnel"][0]

    assert "metric" in funnel_row
    assert "value" in funnel_row


# ============================================================
# Retailrocket propensity
# ============================================================

def test_retailrocket_propensity_contract():
    response = client.get(
        "/api/propensity/retailrocket"
    )

    assert response.status_code == 200

    data = response.json()

    required_top_level = {
        "selection",
        "metrics",
        "ranking",
        "policy",
        "result_source",
    }

    assert required_top_level.issubset(data)

    assert (
        data["result_source"]
        == "results/retailrocket"
    )

    assert len(data["selection"]) > 0
    assert len(data["metrics"]) > 0
    assert len(data["ranking"]) > 0
    assert len(data["policy"]) > 0

    selection = data["selection"][0]

    assert {
        "selected_model",
        "selection_metric",
    }.issubset(selection)

    metric = data["metrics"][0]

    assert {
        "model",
        "split",
        "roc_auc",
        "pr_auc",
    }.issubset(metric)

    policy = data["policy"][0]

    assert {
        "target_pct",
        "lift_vs_population",
        "captured_positive_share",
    }.issubset(policy)


# ============================================================
# Criteo uplift
# ============================================================

def test_criteo_uplift_contract():
    response = client.get(
        "/api/uplift/criteo"
    )

    assert response.status_code == 200

    data = response.json()

    required_top_level = {
        "summary",
        "targeting",
        "model_selection",
        "metrics",
        "deciles",
        "policy",
        "result_source",
    }

    assert required_top_level.issubset(data)

    assert data["result_source"] == "results/criteo"

    summary = data["summary"]

    required_summary_fields = {
        "rows",
        "train_rows",
        "test_rows",
        "mean_predicted_uplift",
        "qini_coefficient",
    }

    assert required_summary_fields.issubset(
        summary
    )

    assert isinstance(data["targeting"], list)
    assert len(data["targeting"]) > 0

    targeting_row = data["targeting"][0]

    required_targeting_fields = {
        "target_fraction",
        "target_pct",
        "rows",
        "treated_conversion_rate",
        "control_conversion_rate",
        "observed_uplift",
        "observed_uplift_pp",
    }

    assert required_targeting_fields.issubset(
        targeting_row
    )
