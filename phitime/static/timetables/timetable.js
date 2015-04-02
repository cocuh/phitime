(function () {
  var TimeTable = {};
  TimeTable.$main = document.getElementById('main');
  TimeTable.columnHeaderElements = [
    document.getElementById('column_header_mon'),
    document.getElementById('column_header_tue'),
    document.getElementById('column_header_wed'),
    document.getElementById('column_header_thr'),
    document.getElementById('column_header_fri'),
    document.getElementById('column_header_sat'),
    document.getElementById('column_header_sun')
  ];
  TimeTable.initCallbacks = function () {
    document.callbacks = {
      refresh: TimeTable.refresh,
      setColumnHeaders: TimeTable.setColumnHeaders
    };
  };
  TimeTable.refresh = function () {
    // TODO: implement here
    alert('refresh!');
  };
  TimeTable.setColumnHeaders = function (headerTexts) {
    for (var idx = 0; idx < TimeTable.columnHeaderElements.length; idx++) {
      var headerText = headerTexts[idx];
      if (headerText !== undefined) {
        var $elem = TimeTable.columnHeaderElements[idx];
        var $textElem = $elem.getElementsByTagName('text')[0];
        $textElem.textContent = headerText;
      }
    }
  };

  var onload = function () {
    TimeTable.initCallbacks();
  };
  window.addEventListener('load', onload);
})();