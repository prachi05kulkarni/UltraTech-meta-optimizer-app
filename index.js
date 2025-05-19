import { useState } from "react";
import axios from "axios";


export default function Home() {
  const [metaTitle, setMetaTitle] = useState("");
  const [metaDescription, setMetaDescription] = useState("");
  const [content, setContent] = useState("");
  const [semanticScore, setSemanticScore] = useState(null);
  const [brainrankScore, setBrainrankScore] = useState(null);
  const [loading, setLoading] = useState(false);

  // Loading states
  const [genMetaLoading, setGenMetaLoading] = useState(false);
  const [enrichLoading, setEnrichLoading] = useState(false);
  const [variantLoading, setVariantLoading] = useState(false);
  const [updateRewardLoading, setUpdateRewardLoading] = useState(false);

  const [selectedVariant, setSelectedVariant] = useState(null);
  const [variantUpdateMessage, setVariantUpdateMessage] = useState("");

  // Generate meta description
  const handleGenerateMeta = async () => {
    if (!content) {
      alert("Please enter content to generate meta description.");
      return;
    }
    setGenMetaLoading(true);
    try {
      const res = await axios.post("http://localhost:5000/generate_meta", {
        content,
      });
      if (res.data.meta_description) {
        setMetaDescription(res.data.meta_description);
      } else {
        alert("Failed to generate meta description.");
      }
    } catch (error) {
      console.error(error);
      alert("Error calling generate_meta endpoint.");
    } finally {
      setGenMetaLoading(false);
    }
  };

  // Enrich meta title and description
  const handleEnrichMeta = async () => {
    if (!metaTitle && !metaDescription) {
      alert("Please enter meta title or description to enrich.");
      return;
    }
    setEnrichLoading(true);
    try {
      const res = await axios.post("http://localhost:5000/enrich_meta", {
        title: metaTitle,
        description: metaDescription,
      });
      if (res.data.enriched_title) {
        setMetaTitle(res.data.enriched_title);
      }
      if (res.data.enriched_description) {
        setMetaDescription(res.data.enriched_description);
      }
    } catch (error) {
      console.error(error);
      alert("Error calling enrich_meta endpoint.");
    } finally {
      setEnrichLoading(false);
    }
  };

  // Select variant using bandit strategy
  const handleSelectVariant = async () => {
    setVariantLoading(true);
    try {
      const res = await axios.get("http://localhost:5000/select_variant");
      if (res.data.selected_variant) {
        setSelectedVariant(res.data.selected_variant);
        setVariantUpdateMessage("");
      } else {
        alert("Failed to select variant.");
      }
    } catch (error) {
      console.error(error);
      alert("Error calling select_variant endpoint.");
    } finally {
      setVariantLoading(false);
    }
  };

  // Update reward for selected variant
  const handleUpdateVariantReward = async () => {
    if (!selectedVariant) {
      alert("No variant selected to update.");
      return;
    }
    setUpdateRewardLoading(true);
    try {
      const res = await axios.post("http://localhost:5000/update_variant", {
        variant: selectedVariant,
        reward: 1,
      });
      if (res.data.message) {
        setVariantUpdateMessage(res.data.message);
      } else {
        alert("Failed to update variant reward.");
      }
    } catch (error) {
      console.error(error);
      alert("Error calling update_variant endpoint.");
    } finally {
      setUpdateRewardLoading(false);
    }
  };

  // Get BrainRank score
  const handleSubmit = async () => {
    setLoading(true);
    setSemanticScore(null);
    setBrainrankScore(null);
    try {
      const response = await axios.post("http://localhost:5000/score", {
        meta_title: metaTitle,
        meta_description: metaDescription,
        content: content,
      });
      setSemanticScore(response.data.semantic_score ?? null);
      setBrainrankScore(response.data.brainrank_score ?? null);
    } catch (error) {
      console.error("Error fetching score:", error);
      alert("Backend is not reachable. Please check your Flask server.");
    } finally {
      setLoading(true);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>BrainRank Scorer & Meta Tools</h1>

      <textarea
        style={styles.input}
        placeholder="Meta Title"
        value={metaTitle}
        onChange={(e) => setMetaTitle(e.target.value)}
      />
      <textarea
        style={styles.input}
        placeholder="Meta Description"
        value={metaDescription}
        onChange={(e) => setMetaDescription(e.target.value)}
      />
      <textarea
        style={{ ...styles.input, height: 150 }}
        placeholder="Page Content"
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />

      <button
        style={styles.button}
        onClick={handleGenerateMeta}
        disabled={genMetaLoading}
      >
        {genMetaLoading ? "Generating Meta..." : "Generate Meta Description"}
      </button>

      <button
        style={styles.button}
        onClick={handleEnrichMeta}
        disabled={enrichLoading}
      >
        {enrichLoading ? "Enriching..." : "Enrich Meta Title & Description"}
      </button>

      {(metaTitle || metaDescription) && (
        <div style={styles.resultBox}>
          <h3>📝 Generated/Enriched Metadata</h3>
          {metaTitle && (
            <p>
              <strong>Title:</strong> {metaTitle}
            </p>
          )}
          {metaDescription && (
            <p>
              <strong>Description:</strong> {metaDescription}
            </p>
          )}
        </div>
      )}

      <button
        style={styles.button}
        onClick={handleSelectVariant}
        disabled={variantLoading}
      >
        {variantLoading ? "Selecting Variant..." : "Select Meta Variant"}
      </button>

      {selectedVariant && (
        <div style={styles.resultBox}>
          <p>
            Selected Variant: <b>{selectedVariant}</b>
          </p>
          <button
            style={styles.button}
            onClick={handleUpdateVariantReward}
            disabled={updateRewardLoading}
          >
            {updateRewardLoading ? "Updating Reward..." : "Send Reward (Click)"}
          </button>
          {variantUpdateMessage && <p>{variantUpdateMessage}</p>}
        </div>
      )}

      <button style={styles.button} onClick={handleSubmit} disabled={loading}>
        {loading ? "Calculating..." : "Get BrainRank Score"}
      </button>

      {semanticScore !== null && (
        <div style={styles.resultBox}>
          <h3>
            🧠 BrainRank Score:{" "}
            <span style={styles.score}>{brainrankScore ?? "N/A"}</span>
          </h3>
          <p>✅ Semantic Score: {semanticScore}</p>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 600,
    margin: "0 auto",
    padding: 20,
    fontFamily: "Arial, sans-serif",
  },
  header: {
    textAlign: "center",
    color: "#333",
  },
  input: {
    width: "100%",
    padding: 10,
    marginBottom: 15,
    fontSize: 16,
    borderRadius: 5,
    border: "1px solid #ccc",
  },
  button: {
    width: "100%",
    padding: 12,
    fontSize: 16,
    backgroundColor: "#0070f3",
    color: "white",
    border: "none",
    borderRadius: 5,
    cursor: "pointer",
    marginBottom: 15,
  },
  resultBox: {
    marginTop: 20,
    padding: 15,
    border: "1px solid #eee",
    borderRadius: 5,
    backgroundColor: "#f9f9f9",
  },
  score: {
    color: "#0070f3",
    fontWeight: "bold",
  },
};
