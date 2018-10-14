var data = source.data;
var filetext = 'Image Index,Finding Labels,PCA_X\n';
for (var i = 0; i < data['Image Index'].length; i++) {
    var currRow = [data['Image Index'][i].toString(),
                   data['Finding Labels'][i].toString(),
                   data['PCA_X'][i].toString().concat('\n')];

    var joined = currRow.join();
    filetext = filetext.concat(joined);
}

var filename = 'data_result.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename);
} else {
    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))
}
