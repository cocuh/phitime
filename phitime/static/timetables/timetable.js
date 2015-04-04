(function () {
  var getElementById = function (id) {
    var elem = document.getElementById(id);
    if (elem === null) {
      throw "the element is not exist(id:" + id + ")";
    }
    return elem;
  };
  var TimeTable = function () {
    this.$timetable = document.getElementById('main');
    this.columnHeaderElements = [
      getElementById('column_header_mon'),
      getElementById('column_header_tue'),
      getElementById('column_header_wed'),
      getElementById('column_header_thr'),
      getElementById('column_header_fri'),
      getElementById('column_header_sat'),
      getElementById('column_header_sun')
    ];
    this.columnElements = [
      getElementById('column_mon'),
      getElementById('column_tue'),
      getElementById('column_wed'),
      getElementById('column_thr'),
      getElementById('column_fri'),
      getElementById('column_sat'),
      getElementById('column_sun')
    ];
    this.classes = {
      cell: 'cell',
      selecting: 'selecting'
    };
    this.cells = document.getElementsByClassName(this.classes.cell);
    this.isEditable = false;
    this.status = {
      start: {
        day: null,
        minY: null,
        maxY: null
      },
      end: {
        day: null,
        minY: null,
        maxY: null
      },
      isSelecting: false
    };
    this._initEventHandler();
  };
  (function (proto) {
    /**
     * set column header texts
     * @param {Array<string>} headerTexts [monday, tuesday, ... , sunday]
     */
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
    // private method
    proto._initEventHandler = function () {
      for (var dayIdx = 0; dayIdx < this.columnElements.length; dayIdx++) {
        var $oneDay = this.columnElements[dayIdx];
        var cellArray = $oneDay.getElementsByClassName(this.classes.cell);
        for (var cellIdx = 0; cellIdx < cellArray.length; cellIdx++) {
          var $cell = cellArray[cellIdx];
          var minY = $cell.getAttribute('y');
          var height = $cell.getBBox().height;
          var eventHandler = this._genEventHandler(dayIdx, minY, height);
          $cell.addEventListener('mousedown', eventHandler.mousedown);
          $cell.addEventListener('mouseover', eventHandler.mouseover);
        }
      }
    };
    proto._genEventHandler = function (dayIdx, minY, height) {
      var that = this;
      var status = this.status;
      var saveStatusStart = function () {
        status.start.day = dayIdx;
        status.start.minY = minY;
        status.start.maxY = minY + height;
      };
      var saveStatusEnd = function () {
        status.end.day = dayIdx;
        status.end.minY = minY;
        status.end.maxY = minY + height;
      };
      var redrawSelecting = function () {
        that._toggleSelectingCellClass(that.classes.selecting, true);
      };
      return {
        mousedown: function (event) {
          saveStatusStart();
          saveStatusEnd();
          status.isSelecting = true;
          redrawSelecting();
          event.preventDefault();
        },
        mouseover: function (event) {
          that._clearSelectingCells();
          if (status.isSelecting && event.buttons != 0 && event.which % 2 != 0) {
            saveStatusEnd();
            redrawSelecting();
          }
          event.preventDefault();
        }
      }
    };
    proto._clearSelectingCells = function () {
      this._toggleSelectingCellClass(this.classes.selecting, false);
    };
    proto._toggleSelectingCellClass = function (className, toggle) {
      for (var cellIdx = 0; cellIdx < this.cells.length; cellIdx++) {
        var $cell = this.cells[cellIdx];
        if (this._isInSelecting($cell)) {
          this._toggleClass($cell, className, toggle);
        }
      }
    };
    proto._toggleClass = function ($elem, className, toggle) {
      if (toggle === undefined) {
        toggle = !this._hasClass($elem, className);
      }
      if (toggle === true) {
        this._addClass($elem, className);
      } else if (toggle === false) {
        this._removeClass($elem, className);
      }
    };
    proto._addClass = function ($elem, className) {
      if (!this._hasClass($elem, className)) {
        $elem.className = $elem.className + ' ' + className;
      }
    };
    proto._removeClass = function ($elem, className) {
      $elem.className = (' ' + $elem.className + ' ').replace(' ' + className + ' ', ' ').trim();
    };
    proto._hasClass = function ($elem, className) {
      return (' ' + $elem.className + ' ').indexOf(' ' + className + ' ') != -1;
    };
    /**
     * is the cell in selecting.
     * @param $cell
     * @return {boolean} is the cell selecting
     */
    proto._isInSelecting = function ($cell) {
      // TODO implement here
    }
  })
  (TimeTable.prototype);

  var onload = function () {
    document.timetable = new TimeTable();
  };
  window.addEventListener('load', onload);
})();