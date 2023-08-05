var ICONS = {
  ok: "glyphicon glyphicon-ok",
  error: "glyphicon glyphicon-remove",
  question: "glyphicon glyphicon-question-sign"
};

var COLORS = {
  ok: 'success',
  error: 'danger',
  warn: 'warning'
};

window.onload = function () {
  var stream = new EventSource('/stream');

  stream.onmessage = function (msg) {
    var data = JSON.parse(msg.data),
        id, icon, color;
    for (id in data) {
      if (data[id]) {
        icon = ICONS.ok;
        color = COLORS.ok;
      } else {
        if (CHECKERS[id].warn) {
          icon = ICONS.question;
          color = COLORS.warn;
        } else {
          icon = ICONS.error;
          color = COLORS.error;
        }
      }
      document.querySelector('#tr-' + id).className = color;
      document.querySelector('#span-' + id).className = icon;
    }
  };
};
