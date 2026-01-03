// Edit this file before deployment.
// For local dev, keep submitUrl as the local receiver.
window.SURVEY_CONFIG = {
  submitUrl: "https://script.google.com/macros/s/AKfycby6laDe4KgN0E0Nf463vUj0tal4QAks6wqt1FEhgAUUSJwkcaQibAhVLPMR2dI0ehFJeg/exec",
  // Google Apps Script 通常不提供 CORS 响应头；用 no-cors 发送“简单请求”可避免 preflight 被拦。
  submitMode: "no-cors", // "cors" | "no-cors"
  completionCodePart1: "C1J3ZVQ3",
  completionCodePart2: "REPLACE_ME_PART2",
  part2: {
    numOld: 20,
    numLures: 20,
  },
};
