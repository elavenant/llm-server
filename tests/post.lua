wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"

math.randomseed(os.time())

local verbs = { "Explain", "Describe", "Summarize", "Translate", "Solve" }
local topics = { "quantum physics", "Napoleon", "blockchain", "artificial intelligence", "cooking pasta" }
local styles = { "in simple terms", "as a poem", "with emojis", "like I'm five", "in one sentence" }

request = function()
  local v = verbs[math.random(#verbs)]
  local t = topics[math.random(#topics)]
  local s = styles[math.random(#styles)]
  local prompt = string.format("%s %s %s.", v, t, s)
  local body = string.format('{"messages":[{"role":"user","content":"%s"}]}', prompt)
  return wrk.format("POST", "/api/chat", nil, body)
end
