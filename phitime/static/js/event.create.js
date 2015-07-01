$(document).ready(function () {
  var timetables = [$("#timetable-0"), $("#timetable-1"), $("#timetable-2"), $("#timetable-3"), $("#timetable-4")];
  (function () {
    var initTimetable = function ($timetable, startDate) {
      var timetable = $timetable[0].contentDocument.timetable;
      timetable.setBaseDate(startDate);
    };
    var currentDate = new Date();
    for (var idx = 0; idx < timetables.length; idx++) {
      var $timetable = timetables[idx];
      if (!$timetable[0].contentDocument.timetable) {
        var generateHandler = function ($theTimetable, theDate) {
          return function () {
            initTimetable($theTimetable, theDate)
          }
        };
        $timetable.on('load', generateHandler($timetable, new Date(currentDate)));
      } else {
        initTimetable($timetable, currentDate);
      }
      currentDate.setDate(currentDate.getDate() + 7);
    }
  })();
  var startDate = new Date();
  var resetTimetablesUrl = function (calendar_path) {
    for (var week_idx = 0; week_idx < timetables.length; week_idx++) {
      var $elem = timetables[week_idx];
      $elem.attr('data', calendar_path);
    }
  };
  var getLatestMonday = function (date) {
    var delta = 7 - (7 + date.getDay() - 1) % 7;
    var res = new Date(date.getTime());
    res.setDate(date.getDate() + delta);
    return res;
  };
  var resetTimetablesHeaders = function (date) {
  };
  $("input[type=radio][name='event.timetable_type']").on('change', function (event) {
    var $target = $(event.target);
    var calendar_path = $target.data('path');
    resetTimetablesUrl(calendar_path);
  });
});