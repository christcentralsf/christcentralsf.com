var interpolate = function(s, o) {
  var placeholder = "";
  for (name in o) {
    placeholder = new RegExp("record." + name + "", "g");
    s = s.replace(placeholder, o[name]);
  }
  return s;
};

var trWriter = function(rowIndex, record, columns, cellWriter) {
  var tr = "<tr>\
              <td>record.date</td>\
              <td class='hidden'>record.sortDate</td>\
              <td><a href='record.mp3' target='_blank'>record.sermon</a></td>\
              <td><a href='http://www.biblegateway.com/passage/?search=record.scripture' target='_blank'>record.scripture</a></td>\
              <td>record.speaker</td>\
              <td>record.series</td>\
              <td align='center'><a href='record.pdf' target='_blank'><i class='fa fa-file'></i></a></td>\
            </tr>";
  return interpolate(tr, record);
};

$(document).ready(function() {
  $("#sermons").dynatable({
    dataset: {
      records: SERMON_FIXTURES,
      perPageDefault: 10,
      perPageOptions: [10, 25, 50, 75, 100]
    },
    writers: {
      _rowWriter: trWriter
    }
  });
});