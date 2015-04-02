(function () {
  var TimeTable = function () {
    this.$timetable = document.getElementById('main');
    this.columnHeaderElements = [
      document.getElementById('column_header_mon'),
      document.getElementById('column_header_tue'),
      document.getElementById('column_header_wed'),
      document.getElementById('column_header_thr'),
      document.getElementById('column_header_fri'),
      document.getElementById('column_header_sat'),
      document.getElementById('column_header_sun')
    ];
  };
  (function (proto) {
    proto.refresh = function () {
      // TODO: implement here
      alert('refresh!');
    };
    proto.setColumnHeaderTexts = function (headerTexts) {
      for (var idx = 0; idx < this.columnHeaderElements.length; idx++) {
        var headerText = headerTexts[idx];
        if (headerText !== undefined) {
          var $elem = this.columnHeaderElements[idx];
          var $textElem = $elem.getElementsByTagName('text')[0];
          $textElem.textContent = headerText;
        }
      }
    };
  })(TimeTable.prototype);

  var onload = function () {
    document.timetable = new TimeTable();
  };
  window.addEventListener('load', onload);
})();