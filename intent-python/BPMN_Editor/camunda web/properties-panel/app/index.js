import $ from 'jquery';
import BpmnModeler from 'bpmn-js/lib/Modeler';

import propertiesPanelModule from 'bpmn-js-properties-panel';
import propertiesProviderModule from 'bpmn-js-properties-panel/lib/provider/camunda';
import camundaModdleDescriptor from 'camunda-bpmn-moddle/resources/camunda.json';

import {
  debounce
} from 'min-dash';

import diagramXML from '../resources/newDiagram.bpmn';


var container = $('#js-drop-zone');

var canvas = $('#js-canvas');

var id;

var bpmnModeler = new BpmnModeler({
  container: canvas,
  propertiesPanel: {
    parent: '#js-properties-panel'
  },
  additionalModules: [
    propertiesPanelModule,
    propertiesProviderModule
  ],
  moddleExtensions: {
    camunda: camundaModdleDescriptor
  }
});
container.removeClass('with-diagram');

window.onload = function() {
  // $('#js-create-diagram').click(function(e) {
  //   e.stopPropagation();
  //   e.preventDefault();
  //   createNewDiagram();
  // });
  id=window.location.href.slice(window.location.href.indexOf('=')+1)
  console.log(id)
  // createNewDiagram();
  getDBDiagram();
};

function createNewDiagram() {
  openDiagram(diagramXML);
}

function openDiagram(xml) {

  bpmnModeler.importXML(xml, function(err) {

    if (err) {
      container
        .removeClass('with-diagram')
        .addClass('with-error');

      container.find('.error pre').text(err.message);

      console.error(err);
    } else {
      container
        .removeClass('with-error')
        .addClass('with-diagram');
    }


  });
}

function saveSVG(done) {
  bpmnModeler.saveSVG(done);
}

function saveDiagram(done) {

  bpmnModeler.saveXML({ format: true }, function(err, xml) {
    done(err, xml);
  });
}

function registerFileDrop(container, callback) {

  function handleFileSelect(e) {
    e.stopPropagation();
    e.preventDefault();

    var files = e.dataTransfer.files;

    var file = files[0];

    var reader = new FileReader();

    reader.onload = function(e) {

      var xml = e.target.result;

      callback(xml);
    };

    reader.readAsText(file);
  }

  function handleDragOver(e) {
    e.stopPropagation();
    e.preventDefault();

    e.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
  }

  container.get(0).addEventListener('dragover', handleDragOver, false);
  container.get(0).addEventListener('drop', handleFileSelect, false);
}


////// file drag / drop ///////////////////////

// check file api availability
if (!window.FileList || !window.FileReader) {
  window.alert(
    'Looks like you use an older browser that does not support drag and drop. ' +
    'Try using Chrome, Firefox or the Internet Explorer > 10.');
} else {
  registerFileDrop(container, openDiagram);
}

function getDBDiagram() {
  
  var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             console.log("this.responseText--> \n"+this.responseText);
             openDiagram(this.responseText);
         }
    };
    // var artifactID =  $('#artifactID').val();
    // alert("URL-->http://localhost:8080/api/artifactsDownload/"+id);
    xhttp.open("GET", "http://localhost:8080/api/artifactsDownload/"+id, true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send();
    

}


// function uploadDiagramDB(){
//   // alert("Start uploading.."+diagramXML);
//   var xhttp = new XMLHttpRequest();
//     xhttp.onreadystatechange = function() {
//          if (this.readyState == 4 && this.status == 200) {
//              alert(this.responseText);
//          }
//     };
//     //var data = "";
    


    
//     xhttp.open("POST", "http://localhost:8080/api/bpmnUpload", true);
    
//     //xhttp.setRequestHeader("Content-type", "application/json");
//     xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
//     xhttp.send("xmlData="+diagramXML);
// }

function uploadDiagramDB(){
  //salert("Start uploading.."+diagramXML);
  var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
             alert(this.responseText);
         }
    };
    //var data = "";
    


    
    xhttp.open("POST", "http://localhost:8080/api/bpmnUpload/"+id, true);
	setTimeout(function(){
		bpmnModeler.saveXML({ format: true }, function(err, xml) {
		
		xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send("xmlData="+xml);
	  });
	  
	},500);
     
    //xhttp.setRequestHeader("Content-type", "application/json");
    
} 


// bootstrap diagram functions

$(function() {

  $('#js-create-diagram').click(function(e) {
    e.stopPropagation();
    e.preventDefault();
    createNewDiagram();
  });


  $('#uploadDiagramDB').click(function(e) {
    e.stopPropagation();
    e.preventDefault();

      uploadDiagramDB();
  });

  $('#getDiagramDB').click(function(e) {
    e.stopPropagation();
    e.preventDefault();

    getDBDiagram();
  });

  var downloadLink = $('#js-download-diagram');
  var downloadSvgLink = $('#js-download-svg');

  $('.buttons a').click(function(e) {
    if (!$(this).is('.active')) {
      e.preventDefault();
      e.stopPropagation();
    }
  });

  function setEncoded(link, name, data) {
    var encodedData = encodeURIComponent(data);

    if (data) {
      link.addClass('active').attr({
        'href': 'data:application/bpmn20-xml;charset=UTF-8,' + encodedData,
        'download': name
      });
    } else {
      link.removeClass('active');
    }
  }

  var exportArtifacts = debounce(function() {

    saveSVG(function(err, svg) {
      setEncoded(downloadSvgLink, 'diagram.svg', err ? null : svg);
    });

    saveDiagram(function(err, xml) {
      setEncoded(downloadLink, 'diagram.bpmn', err ? null : xml);
    });
  }, 500);

  bpmnModeler.on('commandStack.changed', exportArtifacts);
});
