// Simple CV screening API for Cloudflare Workers
export default {
  async fetch(request) {
    // Handle CORS preflight requests
    if (request.method === "OPTIONS") {
      return handleOptions(request);
    }

    // Handle POST requests to /api/screen-cv
    if (request.method === "POST" && new URL(request.url).pathname === "/api/screen-cv") {
      return handleCvScreening(request);
    }

    // Return 404 for other routes
    return new Response("Not found", { status: 404 });
  },
};

// Handle CORS preflight
function handleOptions(request) {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

// Handle CV screening requests
async function handleCvScreening(request) {
  try {
    // Get form data from request
    const formData = await request.formData();
    const cvFile = formData.get("cv");
    const jdText = formData.get("job_description");
    
    // In a real implementation, you would process the CV here
    // For now, we'll return mock data
    
    const results = {
      match_score: "82%",
      verdict: "Strong Match",
      summary: "Candidate has relevant experience in the required technologies and industry.",
      red_flags: ["No certification mentioned", "Short tenure at previous role"]
    };
    
    return new Response(JSON.stringify({
      success: true,
      results: results
    }), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}
