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
      selecting: 'selecting',
      active: 'active',
      unavailable: 'unavailable'
    };
    this.cells = document.getElementsByClassName(this.classes.cell);
    this.isEditable = true;
    this.status = {
      start: {
        day: null,
        minY: null,
        maxY: null,
        $cell: null
      },
      end: {
        day: null,
        minY: null,
        maxY: null,
        $cell: null
      },
      isSelecting: false
    };
    this.startMinutes = parseInt(this.$timetable.getAttribute('data-start'));
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
    /**
     * get active periods, [{startMinutes:startMinutes, periodLength:periodLength}, ...]
     * "startMinutes" means the length of minutes from the midnight.
     * @returns {Object<string, Array<int>>}
     */
    proto.getActivePeriods = function () {
      var activeCellByDay = {};
      var activeCellArray = this._getActiveCells();
      for (var activeCellIdx in activeCellArray) {
        var $activeCell = activeCellArray[activeCellIdx];
        var theDay = this._getCellDay($activeCell);
        var theStartMinutes = this._getCellStartMinutes($activeCell);
        var thePeriodLength = this._getCellPeriodLength($activeCell);
        var theCellData = {startMinutes: theStartMinutes, periodLength: thePeriodLength};
        if (theDay in activeCellByDay) {
          activeCellByDay[theDay].push(theCellData);
        } else {
          activeCellByDay[theDay] = [theCellData];
        }
      }

      for (theDay in activeCellByDay) {
        activeCellByDay[theDay].sort(function (a, b) {
          return a.startMinutes > b.startMinutes ? 1 : -1;
        });
      }

      var res = {};
      for (theDay in activeCellByDay) {
        res[theDay] = activeCellByDay[theDay].reduce(function (previousValue, currentValue, index, array) {
          if (previousValue.length == 0) {
            return [currentValue];
          }
          var lastMinutes = previousValue[previousValue.length - 1].startMinutes;
          var lastLength = previousValue[previousValue.length - 1].periodLength;
          if (lastMinutes + lastLength == currentValue.startMinutes) {// current y
            previousValue[previousValue.length - 1].periodLength += currentValue.periodLength;
          } else {
            previousValue.push(currentValue);
          }
          return previousValue;
        }, []);

      }

      return res;
    };
    /**
     * set editable or not
     * @param {bool} [isEditable] next isEditable flag. default is toggle.
     * @returns {bool}
     */
    proto.setEditable = function (isEditable) {
      if (isEditable === undefined) {
        isEditable = !this.isEditable;
      }
      this.isEditable = isEditable;
      return isEditable;
    };
    /**
     * set unavailable periods, neither update or append.
     * "startMinutes" means the length of minutes from the midnight.
     *
     * @param {Array<Array<Object<str,int>>>} periodByDay [monday_period_list, tuesday_period_list....], period_list:=[{startMinutes: startMinutes, periodLength:length},]
     */
    proto.setUnavailablePeriods = function (periodByDay) {
      var self = this;
      this._mapEachCell(function ($cell, cellIdx, $oneDay, dayIdx) {
        var cellStartMinutes = self._getCellStartMinutes($cell);
        var periodLength = self._getCellPeriodLength($cell);
        var cellEndMinutes = cellStartMinutes + periodLength;
        var theDayUnavailablePeriods = periodByDay[dayIdx];
        if (theDayUnavailablePeriods) {
          theDayUnavailablePeriods.forEach(function (period) {
            if (!(cellEndMinutes <= period.startMinutes
              || period.startMinutes + period.periodLength <= cellStartMinutes)) {
              self._addClass($cell, self.classes.unavailable);
            }
          });
        }
      });
    };
    // private method
    proto._mapEachCell = function (func) {
      for (var dayIdx = 0; dayIdx < this.columnElements.length; dayIdx++) {
        var $oneDay = this.columnElements[dayIdx];
        var cellArray = $oneDay.getElementsByClassName(this.classes.cell);
        for (var cellIdx = 0; cellIdx < cellArray.length; cellIdx++) {
          var $cell = cellArray[cellIdx];
          func($cell, cellIdx, $oneDay, dayIdx);
        }
      }
    };
    proto._initEventHandler = function () {
      var self = this;
      var initEventHandler = function ($cell, cellIdx, $oneDay, dayIdx) {
        var minY = self._getCellStartMinutes($cell);
        var height = self._getCellPeriodLength($cell);
        var eventHandler = self._genCellEventHandler(dayIdx, minY, height, $cell);
        $cell.addEventListener('mousedown', eventHandler.mousedown);
        $cell.addEventListener('touchstart', eventHandler.mousedown);
        $cell.addEventListener('mouseover', eventHandler.mouseover);
        $cell.addEventListener('touchmove', eventHandler.mouseover);
        $cell.addEventListener('gesturechange', eventHandler.mouseover);
        $cell.addEventListener('gesturemove', eventHandler.mouseover);
      };
      this._mapEachCell(initEventHandler);
      document.addEventListener('mouseup', this._genMouseUpHandler());
      document.addEventListener('touchend', this._genMouseUpHandler());
      document.addEventListener('gestureend', this._genMouseUpHandler());
    };
    proto._genMouseUpHandler = function () {
      var self = this;
      return function () {
        if (self.status.start.$cell && self.status.end.$cell) {
          var isActive = self._hasClass(self.status.start.$cell, self.classes.active);
          self._toggleSelectingCellClass(self.classes.active, !isActive);
          self._clearSelectingCells();
        }
        self.status.isSelecting = false;
        self.status.start.day = 0;
        self.status.start.minY = 0;
        self.status.start.maxY = 0;
        self.status.start.$cell = 0;
        self.status.end.day = 0;
        self.status.end.minY = 0;
        self.status.end.maxY = 0;
        self.status.end.$cell = 0;
      }
    };
    proto._genCellEventHandler = function (dayIdx, minY, height, $cell) {
      var self = this;
      var status = this.status;
      var saveStatusStart = function () {
        status.start.day = dayIdx;
        status.start.minY = minY;
        status.start.maxY = minY + height;
        status.start.$cell = $cell;
      };
      var saveStatusEnd = function () {
        status.end.day = dayIdx;
        status.end.minY = minY;
        status.end.maxY = minY + height;
        status.end.$cell = $cell;
      };
      var redrawSelecting = function () {
        self._toggleSelectingCellClass(self.classes.selecting, true);
      };
      return {
        mousedown: function (event) {
          if (!self.isEditable) {
            return true;
          }
          saveStatusStart();
          saveStatusEnd();
          status.isSelecting = true;
          redrawSelecting();
          event.preventDefault();
          return false;
        },
        mouseover: function (event) {
          self._clearSelectingCells();
          console.log(event.touches)
          if (status.isSelecting && event.buttons != 0 && event.which % 2 != 0) {
            saveStatusEnd();
          }
          redrawSelecting();
          event.preventDefault();
          return false;
        }
      }
    };
    /**
     *
     * @private {Array<DOMElement>}
     */
    proto._getActiveCells = function () {
      var activeCells = [];
      for (var idx = 0; idx < this.cells.length; idx++) {
        var $cell = this.cells[idx];
        if (this._hasClass($cell, this.classes.active) && !this._hasClass($cell, this.classes.unavailable)) {
          activeCells.push($cell);
        }
      }
      return activeCells;
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
    proto._getClassName = function ($elem) {
      return $elem.classname.indexOf ? $elem.className : $elem.className.baseVal;
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
        $elem.className.baseVal += ' ' + className;
      }
    };
    proto._removeClass = function ($elem, className) {
      $elem.className.baseVal = (' ' + $elem.className.baseVal + ' ').replace(' ' + className + ' ', ' ').trim();
    };
    proto._hasClass = function ($elem, className) {
      return (' ' + $elem.className.baseVal + ' ').indexOf(' ' + className + ' ') >= 0;
    };
    /**
     * is the cell in selecting.
     * @param $cell
     * @return {boolean} is the cell selecting
     */
    proto._isInSelecting = function ($cell) {
      if (this._hasClass($cell, this.classes.unavailable)) {
        return false;
      }

      var minDay = Math.min(this.status.start.day, this.status.end.day);
      var maxDay = Math.max(this.status.start.day, this.status.end.day);
      var theDay = this._getCellDay($cell);

      if (theDay < minDay || maxDay < theDay) {
        return false;
      }
      // else
      // minDay <= theDay <= maxDay

      var minY = Math.min(this.status.start.minY, this.status.end.minY);
      var maxY = Math.max(this.status.start.maxY, this.status.end.maxY);
      var theY = this._getCellStartMinutes($cell);
      var height = this._getCellPeriodLength($cell);

      if (minY <= theY && theY + height <= maxY) {
        return true;
      }
      return false;
    };
    /**
     * @param $cell
     * @private
     * @returns {int}
     */
    proto._getCellStartMinutes = function ($cell) {
      return parseInt($cell.getAttribute('data-y')) + this.startMinutes;
    };
    /**
     * @param $cell
     * @private
     * @returns {int}
     */
    proto._getCellPeriodLength = function ($cell) {
      return parseInt($cell.getAttribute('data-height'));
    };
    /**
     * @param $cell
     * @private
     * @returns {int}
     */
    proto._getCellDay = function ($cell) {
      return parseInt($cell.getAttribute('data-day'));
    }
  })(TimeTable.prototype);

  var onload = function () {
    document.timetable = new TimeTable();
  };
  window.addEventListener('load', onload);
})();