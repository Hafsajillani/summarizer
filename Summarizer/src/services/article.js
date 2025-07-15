const apiKey = import.meta.env.GEMINI_API_KEY;
const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${apiKey}`;

// Helper to extract main text from HTML
function extractMainText(html) {
  try {
    const doc = new DOMParser().parseFromString(html, "text/html");
    // Get all paragraphs and join them
    const paragraphs = Array.from(doc.querySelectorAll("p"))
      .map((p) => p.textContent.trim())
      .filter(Boolean)
      .join(" ");
    return paragraphs;
  } catch (e) {
    return '';
  }
}

export const getSummary = async (url) => {
  try {
    const response = await fetch("http://localhost:5000/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    if (!response.ok) {
      let errorMsg = "Something went wrong. Please try again later.";
      try {
        const errorData = await response.json();
        // Check for quota or rate limit errors
        if (errorData.error && errorData.error.includes("429")) {
          errorMsg = "You have exceeded your Gemini API quota. Please wait and try again later, or upgrade your plan.";
        } else if (errorData.error && errorData.error.includes("400")) {
          errorMsg = "There was a problem with the request. Please check the article link or try a different one.";
        }
      } catch (e) {
        // fallback to default error message
      }
      throw new Error(errorMsg);
    }
    const data = await response.json();
    return data.summary || "";
  } catch (error) {
    // Only show user-friendly error messages
    throw new Error(error.message || "Something went wrong. Please try again later.");
  }
};