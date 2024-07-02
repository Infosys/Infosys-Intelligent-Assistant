/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, Input, OnInit, ElementRef, Output, EventEmitter } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { ViewEncapsulation, ViewChild } from '@angular/core';
import { OpenTicketsComponent } from '../open-tickets/open-tickets.component';
import { LoaderComponent } from '../../loader/loader.component'
import { ScriptsPopupComponent } from '../scripts-popup/scripts-popup.component';
import { MatTableDataSource, MatPaginator, MatSort, MatPaginatorModule, MatTableModule, MatDialog } from '@angular/material';
import { LogsComponent } from '../logs/logs.component'
import { DiagComponent } from '../diag-popup/diag-popup.component'
import { ArgsComponent } from '../arg-popup/arg-popup.component'
import { OrchestratorArgsPopupComponent } from '../orchestrator-args-popup/orchestrator-args-popup.component'
import { TagInputModule } from 'ngx-chips';
import { AnnotationModalComponent } from '../modal-annotation/modal-annotation.component';
import { ImagePreviewerComponent } from '../image-previewer/image-previewer.component';
import { ImageViewerConfig, CustomEvent } from 'ngx-image-viewer/src/app/image-viewer/image-viewer-config.model';
import { CreateScriptComponent } from '../../admin/create-script/create-script.component'
import { ValidationMessageComponent } from '../../resource-planning/validation-message/validation-message.component';
import { RelatedTicketsModalComponent } from './related-tickets-modal/related-tickets-modal.component';
import { ImageOneShotModalComponent } from './imageoneshot-modal/imageoneshot-modal.component';
import { map } from 'rxjs/operators';
import { Router } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';
import { Pipe, PipeTransform } from '@angular/core';
import { RpaPopupComponent } from '../rpa-popup/rpa-popup.component'
import { CreateRPAComponent } from 'app/admin/create-rpa/create-rpa.component';
import { RpaDiagPopupComponent } from '../rpa-diag-popup/rpa-diag-popup.component';
export interface UserData {
  name: string;
  type: string;
  source: string;
  environment: string;
  incident_no: string;
  desc_key: string;
  orchestrator_args_list: any[];
  score: string;
  invoke: string;
}
@Component({
  selector: 'related-tickets',
  templateUrl: './related-tickets.component.html',
  styleUrls: ['./related-tickets.component.css'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '(document:click)': 'onOutsideClick($event)'
  }
})
export class RelatedTicketsComponent implements OnInit {
  @Output() emitService = new EventEmitter();
  @Input() dataToTakeAsInput: any;
  displayedColumns: string[] = ['name', 'type', 'source', 'environment', 'incident_no', 'desc_key', 'score', 'invoke'];
  dataSource: MatTableDataSource<UserData>;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  private customerId: number = 1;
  private relatedTickets: any = [];
  private copyRelatedTickets: any = [];
  private highlitedTickets: any = [];
  private knownErrors: any = [];
  private knowledgeInfo: any = [];
  private kbArticleInfo: any = [];
  wordcloudsample: any = [];
  showCloud = false;
  showHistory = false;
  showApprove = false;
  predictedFields: any = [];
  namedEntities: any = [];
  imagenamedEntities: any = [];
  EntityEnabled = false;
  otherFields: any = [];
  allFields: any = [];
  allValues: any = [];
  predictedTicketsData: any = [];
  incidentTicketsData: any = [];
  datasetName: string = "";
  allDatasetNames: any = [];
  predictedApprovedDetails: any = [];
  approveSuccess: boolean = false;
  loading: boolean = false;
  predAssigneeStatus: boolean = false;
  summaryShowHide = true;
  relatedTicketsShowHide = false;
  resolutionsShowHide = false;
  detailedAnalysisShowHide = false;
  ShowWordCloud = false;
  private openTickets: any = [];
  openticketsCount: Number;
  closeResult: string;
  tagCloudData = [];
  cloudType: string = "Unigram";
  rawTicketData: any = [];
  scriptStatus: boolean;
  resolutionHistory: any;
  message: string;
  type: string;
  logs = {};
  resolutionHistoryKeys: any;
  selectedAll: any;
  envList = ['Local']
  auditLogs: any = []
  public resInfo: UserData[] = [];
  emailstring: string = "mailto:testmail?Subject=Reg. Ticket - Need more Details&body=Hello,<br><br>This is regarding the ticket raised in appname from your ID. Please share more details on the ticket. Thank you.<br><br>Regards,<br>Test";
  private myArrayColor: any = ["#00695c", "#1C2331", "#d50000", "#1b5e20", "#e65100", "#212121", "#3e2723",
    "#000000", "#1c2331"];
  contributingWords: any;
  tags: any = []
  attachmentsData: any = [];
  resolutionSteps: any = {};
  attachmentsState: boolean = false;
  kbSourcename: any = [];
  ticketclosestatus: any = [];
  queryWords: any = [];
  words: any[];
  dup: any = [];
  repeatWords: any = [];
  emptyWords: any = [];
  saveSuccess: boolean = false;
  toBeEdittedScript: string;
  diagList: any = [];
  argTypes: any = [];
  images: any = [];
  imagestate: boolean = false;
  ApproveLoading = false;
  config: ImageViewerConfig = { customBtns: [{ name: 'next', icon: 'fa fa-arrow-right' }, { name: 'previous', icon: 'fa fa-arrow-left' }] };
  imageIndexOne: number = 0;
  imageIndex: number = 0;
  demo = true;
  trainimageSuccess: boolean = false;
  resolutionColumns: any = [];
  filesCount: number;
  filesStatus: string;
  downloadimage: string;
  RTChosenAlgorithm: string;
  snowinstance: any;
  chosenTeam: string;
  teams: any = [];
  constructor(
    private httpClient: HttpClient,
    private httpService: HttpClient,
    private modalService: NgbModal,
    public activeModal: NgbActiveModal,
    private _eref: ElementRef,
    public dialog: MatDialog,
    private router: Router
  ) {
    TagInputModule.withDefaults({
      tagInput: {
        placeholder: 'Add a new stopword',
        // add here other default values for tag-input
      },
      dropdown: {
        displayBy: 'my-display-value',
        // add here other default values for tag-input-dropdown
      }
    });
  }
  ngOnInit() {
    //team change
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.teams = data['Teams'];
        this.httpService.get('/api/getApplicationTeamNames', { responseType: 'text' }).subscribe(team => {
          if (team != 'no team') {
            this.chosenTeam = team;
            this.getStatus();
          }
        });
      } else {
        console.log('No Dataset found!. Create Dataset to proceed with uploading of assignment details');
      }
    }, err => {
      console.log(err);
      throw '';
    });
    //team change
    this.getSNOWInstance();
    //to get open tickets count
    this.httpClient.get('/api/getRelatedOpenTickets/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + this.dataToTakeAsInput['IncidentNumber'])
      .subscribe(data => {
        this.openTickets = data;
        this.openticketsCount = this.openTickets.length;
      },
        err => {
          console.log(err);
          throw "";
        });
    //to get contributing words
    this.httpClient.get('/api/importantFeaturesReport/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + this.dataToTakeAsInput['IncidentNumber'])
      .subscribe(data => {
        this.contributingWords = data
        for (let key in data) {
          //values are combination of contributing words and weight we need to sepearate 
          for (var i = 0; i < data[key].length; i++) {
            let words = data[key][i];
            this.queryWords.push(words[0]);
            if (!(this.queryWords.includes(words[0]))) {
              this.queryWords.push(words[0]);
            }
          }
          let findDuplicates = arr => arr.filter((item, index) => arr.indexOf(item) != index)
          this.dup = findDuplicates(this.queryWords)
          //removing multiple in dup array 
          for (var i = 0; i < this.dup.length; i++) {
            if (!(this.repeatWords.includes(this.dup[i]))) {
              this.repeatWords.push(this.dup[i]);
            }
          }
          console.log("repeating contibuting words  for this key are ", this.repeatWords);
          if ((this.repeatWords).length > 4) {
            (this.repeatWords).splice(3, (this.repeatWords).length)
          }
        }
      },
        err => {
          console.log(err);
          throw "";
        });
    this.httpClient.get('/api/getdefaultSourceDetails').subscribe(data => {
      if (data['Related_Tickets_Algorithm'] != undefined) this.RTChosenAlgorithm = data['Related_Tickets_Algorithm'];
      else this.RTChosenAlgorithm = 'textrank';
    });
    this.rawTicketData = this.dataToTakeAsInput['rawTicketData'];
    if (this.dataToTakeAsInput['PredictRadio'] != "ITSM") {
      this.getPredictedTickets(this.customerId);
    }
    this.getStatus();
    this.getNamedEntities();
    this.emailstring = "mailto:testmail?Subject=Reg. Ticket - " + this.dataToTakeAsInput['IncidentNumber'] + "-  Need more Details&body=Hello,%0A%0AThis is regarding the ticket raised from your ID -" + this.dataToTakeAsInput['IncidentNumber'] + " - " + this.dataToTakeAsInput['Description'] + "%0APlease share more details or attach any screenshots related to this ticket. Thank you.%0A%0AWith Best Regards,%0ATest";
    //for audit logs
    this.httpClient.get('/api/getAuditLogs/' + this.dataToTakeAsInput["IncidentNumber"]).subscribe(data => {
      this.auditLogs = data;
      this.auditLogs.reverse()
    });
    //for getting tags
    this.httpClient.get('/api/Tags/' + this.dataToTakeAsInput['IncidentNumber'] + '/' + this.customerId + '/' + this.dataToTakeAsInput['DatasetID']).subscribe(data => {
      this.tags = data;
    });
    //to get kbsourcename 
    this.httpClient.get("/api/getDefaultKBSource")
      .subscribe(sdata => {
        this.kbSourcename = sdata['DefaultKBSource'];
      });
    this.getImagesOnScreen();
    this.getAttachmentdata(this.dataToTakeAsInput['IncidentNumber'] + "_" + (this.imageIndex + 1));
    //to get image NER entities 
    this.getImageNERData(this.dataToTakeAsInput['IncidentNumber'] + "_" + (this.imageIndex + 1));
  }
  gonext(event) {
  }
  goprevious(event) {
  }
  handleEvent(event: CustomEvent) {
    switch (event.name) {
      case 'print':
        break;
      case 'download':
        let img_obj = this.images[this.imageIndex];
        break;
      case 'next':
        if (this.imageIndex < this.images.length - 1) {
          this.imageIndex++; //0,1,2 starts from 0
          this.loading = true;
          this.attachmentsState = false;
          this.getAttachmentdata(this.dataToTakeAsInput['IncidentNumber'] + "_" + (this.imageIndex + 1));//to map with images array +1
          this.getImageNERData(this.dataToTakeAsInput['IncidentNumber'] + "_" + (this.imageIndex + 1));
        }
        break;
      case 'previous':
        if (this.imageIndex > 0) {
          this.imageIndex--;
          this.loading = true;
          this.attachmentsState = false;
          this.getAttachmentdata(this.dataToTakeAsInput['IncidentNumber'] + "_" + (this.imageIndex + 1));//to map with images array +1
          this.getImageNERData(this.dataToTakeAsInput['IncidentNumber'] + "_" + (this.imageIndex + 1));
        }
        else {
          console.log("reached first image, disable previous arrow");
        }
        break;
    }
  }
  getImagesOnScreen() {
    this.httpClient.get('/api/getFilesCount/' + this.dataToTakeAsInput['IncidentNumber'])
      .subscribe(data => {
        this.filesStatus = data['status']
        if (this.filesStatus == 'success') {
          this.filesCount = data['count'];
          for (let i = 1; i <= this.filesCount; i++) {
            this.images.push('assets/uploads/' + this.dataToTakeAsInput['IncidentNumber'] + "/" + this.dataToTakeAsInput['IncidentNumber'] + "_" + i + '.PNG');
          }
        }
        else {
          //means there no files or no folder exists with this incident number so setting image state =false
          this.imagestate = false;
        }
        if (this.images.length == 0) {
          this.imagestate = false;
        }
        else {
          this.imagestate = true;
        }
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  getSNOWInstance() {
    this.httpClient.get("/api/getCurrentSnowInstance").subscribe(data => {
      this.snowinstance = data['SNOWInstance']
    })
  }
  getImageNERData(image_name) {
    this.httpClient.get('/api/getImageNERData/' + this.dataToTakeAsInput['IncidentNumber'] + "/" + image_name).subscribe(data => {
      if (data != null) {
        this.imagenamedEntities = data;
      }
    },
      err => {
        console.log("imageENtities data in err")
        console.log(err);
        throw "";
      });
  }
  getAttachmentdata(image_name) {
    this.loading = true;
    this.attachmentsData = [];
    this.resolutionColumns = [];
    this.httpClient.get('/api/getAttachmentsData/' + this.dataToTakeAsInput['IncidentNumber'] + "/" + image_name).subscribe(data => {
      if (data != null) {
        this.attachmentsState = true;
        this.attachmentsData = data;
        this.loading = false;
        for (let key in this.attachmentsData) {
          this.resolutionColumns.push(key);
        }
      } else {
        this.loading = false;
        this.attachmentsState = false;
      }
    }, err => {
      this.loading = false;
      this.attachmentsState = false;
      this.downloadimage = "/assets/uploads" + "/" + this.dataToTakeAsInput['IncidentNumber'] + "/" + image_name + ".PNG";
    });
    this.httpClient.get("/api/getCurrentSnowInstance").subscribe(data => {
      this.snowinstance = data
    })
  }
  getKBSourceName() {
    this.httpClient.get("/api/getDefaultKBSource/")
      .subscribe(sdata => {
        this.kbSourcename = sdata['DefaultKBSource'];
      });
  }
  private getNamedEntities() {
    if (this.namedEntities.length == 0) {
      this.httpClient.get('/api/getNER/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + this.dataToTakeAsInput['IncidentNumber'])
        .subscribe(data => {
          this.namedEntities = data;
          if (this.namedEntities.length > 0) {
            this.EntityEnabled = true;
          }
        },
          err => {
            console.log(err);
            throw "";
          });
    }
  }
  entityValueToUpdate(event, id: number) {
    let newEntities = ((event.target.textContent).trim()).split(',');
    this.namedEntities[id]['Value'] = [];
    event.target.textContent = '';
    newEntities.forEach(entity => {
      if (entity.trim() != '') {
        this.namedEntities[id]['Value'].push(entity.trim());
        event.target.textContent = event.target.textContent + entity.trim() + ', ';
      }
    });
  }
  updateEntityValues() {
    this.httpClient.put('api/updateNER/' + this.customerId + '/' + this.dataToTakeAsInput['DatasetID'] + '/' + this.dataToTakeAsInput['IncidentNumber'], this.namedEntities, { 'responseType': 'text' })
      .subscribe(msg => {
        if (msg == 'success') {
          this.getNamedEntities();
        } else {
          console.warn('Could not Add/Update new Entity Values! failure resp from api');
        }
      }, err => {
        console.error(err);
      });
  }
  private getPredictedTickets(custID: number) {
    this.incidentTicketsData = [];
    this.httpClient.get('/api/predictedTickets/' + custID + "/" + this.dataToTakeAsInput['DatasetID']).subscribe(data => {
      this.predictedTicketsData = data;
      this.getAllFields(custID);
      this.predictedTicketsData.forEach(ticket => {
        ticket['Selected'] = false;
        if (ticket["number"] === this.dataToTakeAsInput['IncidentNumber']) {
          this.showApprove = true;
          this.rawTicketData.forEach((field, index) => {
            Object.keys(field).forEach((key) => {
              ticket[key] = field[key];
            });
          });
          this.incidentTicketsData.push(ticket);
        }
      });
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  applyFilter(filterValue: string) {
    this.dataSource.filter = filterValue.trim().toLowerCase();
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }
  private getAllFields(custID: number) {
    this.allFields = [];
    this.httpClient.get('/api/getDatasetDetails/' + custID + "/" + this.dataToTakeAsInput['DatasetID']).subscribe(data => {
      if (data && data['name'] === "") {
      } else {
        this.datasetName = data['name'];
        let temp = data['fields'];
        temp.forEach((attribute, index) => {
          this.allFields.push(attribute);
        })
        let assignee = this.allFields.find(attribute => attribute === "assigned_to");
        let index_assignee = this.allFields.indexOf(assignee);
        this.allFields.splice(index_assignee, 1);
        let ticketNumber = this.allFields.find(attribute => attribute === "number");
        let index_ticketNumber = this.allFields.indexOf(ticketNumber);
        this.allFields.splice(index_ticketNumber, 1);
        this.httpClient.get('/api/allDatasetNames/' + custID).subscribe(data => {
          this.allDatasetNames = data;
        });
        this.getPredictedFields(custID);
      }
    });
  }
  private getPredictedFields(custID: number) {
    this.predictedFields = [];
    this.otherFields = [];
    //get Predicted Fields list from TblCustomer based on Customer ID
    this.httpClient.get('/api/predictedfields/' + custID + "/" + this.chosenTeam).subscribe(data => {
      data['FieldSelections'].forEach((selection) => {
        if (selection['FieldsStatus'] == "Approved") {
          let temp = selection['PredictedFields'];
          temp.forEach((field) => {
            this.predictedFields.push(field.PredictedFieldName);
          });
        }
      });
      this.predictedFields.forEach(predictedField => {
        let field = this.allFields.find(attribute => attribute === predictedField);
        let index_field = this.allFields.indexOf(field);
        this.allFields.splice(index_field, 1);
        this.otherFields.push(predictedField);
      });
      this.predictedFields.forEach(field => {
        this.httpClient.get('/api/allValues/' + custID + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + field).subscribe(data => {
          this.allValues[field] = data;
          console.log("all values are " + this.allValues);
        });
      })
    });
  }
  private approveTicket() {
    this.loading = true;
    this.approveSuccess = false;
    this.predictedApprovedDetails = {};
    let temp = [];
    let selectedTickets = [];
    this.incidentTicketsData.forEach(predictedTicket => {
      predictedTicket.Selected = true;
      selectedTickets.push(predictedTicket);
    })
    selectedTickets.forEach(selectedTicket => {
      this.predictedApprovedDetails = {};
      this.predictedApprovedDetails['number'] = selectedTicket['number'];
      this.predictedApprovedDetails['predicted_assigned_to'] = selectedTicket['predicted_assigned_to'].toString();
      this.predictedFields.forEach((field, index) => {
        this.predictedApprovedDetails[field] = selectedTicket['predicted_fields'][index][field];
      });
      temp.push(this.predictedApprovedDetails);
    });
    this.ApproveLoading = true;
    this.emitService.next(this.ApproveLoading)
    this.httpClient.put('/api/updatePredictedDetails/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'], temp, { responseType: 'text' })
      .subscribe(msg => {
        msg = JSON.parse(msg)
        if (msg[0]['Status'] == 'success') {
          this.ApproveLoading = false;
          this.approveSuccess = true;
          console.log(msg);
          this.activeModal.dismiss({ "ApproveLoading": this.ApproveLoading });
        }
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  private predictedFieldValueChange(ticket: string, field: string, value: string) {
    if (field == 'assignment_group') {
      this.httpClient.get(encodeURI('/api/findpossibleassignees/' + ticket + '/' + encodeURIComponent(value))).subscribe(data => {
        this.incidentTicketsData.forEach(predictedTicket => {
          if (predictedTicket['number'] == ticket) {
            predictedTicket['possible_assignees'] = data['possibleAssignees'];
            predictedTicket['predicted_assigned_to'] = data['predictedAssignedTo'];
            console.log(predictedTicket['possible_assignees']);
          }
        })
      });
    }
  }
  private assignedToChange(ticket: string, value: string) {
  }
  displayResolutionWordCloud(ticketNumber: string, tabName: string) {
    this.httpClient.get('/api/display_resolution/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + ticketNumber + "/" + tabName + "/" + this.cloudType + "/" + this.RTChosenAlgorithm)
      .subscribe(data => {
        if (data) {
          this.showCloud = true;
          this.tagCloudData = [];
          this.wordcloudsample = data;
          for (var key in this.wordcloudsample) {
            var randomItem = this.myArrayColor[Math.floor(Math.random() * this.myArrayColor.length)];
            this.tagCloudData.push({ text: key + '(' + this.wordcloudsample[key] + ')', weight: (this.wordcloudsample[key]), color: randomItem });
          }
        }
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  ZoomOnHoverOptions = {
    scale: 1.6, // Elements will become 130 % of current zize on hover
    transitionTime: 0.3, // it will take 1.2 seconds until the zoom level defined in scale property has been reached
    delay: 0.1 // Zoom will take affect after 0.8 seconds
  };
  cloudoptions: CloudOptions = {
    // if width is between 0 and 1 it will be set to the size of the upper element multiplied by the value 
    width: 0.8,
    height: 450,
    overflow: false,
    randomizeAngle: false,
    zoomOnHover: this.ZoomOnHoverOptions,
    realignOnResize: true,
  };
  open(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: "lg" }).result.then((result) => {
      this.closeResult = 'Closed with: ${result}';
    });
  }
  showSummary() {
    this.summaryShowHide = true;
    this.relatedTicketsShowHide = false;
    this.resolutionsShowHide = false;
    this.detailedAnalysisShowHide = false;
  }
  showRelated() {
    this.relatedTickets = [];
    if (this.relatedTickets.length == 0) {
      this.httpClient.get('/api/getRelatedTickets/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + this.dataToTakeAsInput['IncidentNumber'] + "/" + this.RTChosenAlgorithm)
        .subscribe(data => {
          this.relatedTickets = data;
          this.copyRelatedTickets = this.relatedTickets;
          if (this.relatedTickets != "No Results Found") {
            this.relatedTickets.forEach(ticket => {
              ticket['highlight'] = false;
            });
          }
        },
          err => {
            console.log(err);
            throw "";
          });
    }
    //Known Errors
    if (this.knownErrors.length == 0) {
      this.httpClient.get('/api/getKnownErrors/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + this.dataToTakeAsInput['IncidentNumber'])
        .subscribe(data1 => {
          this.knownErrors = data1;
        },
          err => {
            console.log(err);
            throw "";
          });
    }
    //Knowledge Info
    this.loading = true;
    let formData = new FormData();
    formData.append('word', JSON.stringify(this.repeatWords));
    console.log("formdata sending from front end is", formData)
    this.httpClient.get('/api/getRelatedKnowledgeArticles/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + this.dataToTakeAsInput['IncidentNumber'] + "/" + this.RTChosenAlgorithm)
      .subscribe(data3 => {
        this.knowledgeInfo = data3;
        console.log(data3);
        this.loading = false;
      },
        err => {
          console.log(err);
          throw "";
        });
    this.summaryShowHide = false;
    this.relatedTicketsShowHide = true;
    this.resolutionsShowHide = false;
    this.detailedAnalysisShowHide = false;
    if (this.relatedTickets == "No Results Found") {
      alert('There are no related tickets for this ticket');
    }
  }
  showDetailedAnalysis() {
    this.summaryShowHide = false;
    this.relatedTicketsShowHide = false;
    this.resolutionsShowHide = false;
    this.detailedAnalysisShowHide = true;
  }
  showResolutions() {
    let tempList: any = []
    this.envList = ['Local']
    this.httpClient.get("/api/getEnvironments").subscribe(data => {
      tempList = data
      tempList.forEach(element => {
        this.envList.push(element['name'])
      });
    })
    let formdata = new FormData()
    formdata.append('Number', this.dataToTakeAsInput['IncidentNumber'])
    formdata.append('Desc', this.dataToTakeAsInput['Description'])
    formdata.append('Tags', JSON.stringify(this.tags))
    this.httpClient.post('/api/getPossibleResolutions', formdata).subscribe(data => {
      this.resolutionHistory = []
      this.resInfo = []
      this.resolutionHistory = data
      let input_params_list = [];
      this.resolutionHistory.forEach(element => {
        if (element['type'] == "orchestrator") {
          input_params_list = element['input_params_list'];
        } else {
          input_params_list = [];
        }
        if (element['score'] == 0) {
          this.resInfo.push({ name: element['name'], type: element["type"], source: element["source"], environment: 'Local', incident_no: element["incident_no"], desc_key: element["description"], orchestrator_args_list: input_params_list, score: 'Nil', invoke: '' })
        } else {
          this.resInfo.push({ name: element['name'], type: element["type"], source: element["source"], environment: 'Local', incident_no: element["incident_no"], desc_key: element["description"], orchestrator_args_list: input_params_list, score: element["score"], invoke: '' })
        }
      });
      // Assign the data to the data source for the table to render
      this.dataSource = new MatTableDataSource(this.resInfo)
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    })
    this.summaryShowHide = false;
    this.relatedTicketsShowHide = false;
    this.resolutionsShowHide = true;
    this.detailedAnalysisShowHide = false;
  }
  invokeResolution(row: any, type: any) {
    if (row['type'] == 'script') {
      this.logs = {}
      let formData = new FormData();
      formData.append('ScriptName', row["name"]);
      formData.append('Environment', row["environment"])
      formData.append('Type', type)
      this.httpClient.post("/api/invokeIopsScripts", formData, { responseType: 'text' }).subscribe(data => {
        this.logs[row["name"]] = data;
        this.type = 'success';
        this.message = "Operation Completed";
        this.scriptStatus = true;
        if (!(data.toLowerCase().includes('exception')) && !(data.toLowerCase().includes('err')) && !(data.toLowerCase().includes('error')) && !(data.toLowerCase().includes('access denied'))) {
          this.SaveResolutionDetails(row['type'], row["name"], 'success', 'Running Script : ' + data)
        } else {
          this.SaveResolutionDetails(row['type'], row["name"], 'failure', 'Running Script : ' + data)
        }
        this.httpClient.get('/api/getAuditLogs/' + this.dataToTakeAsInput["IncidentNumber"]).subscribe(data => {
          this.auditLogs = data;
          this.auditLogs.reverse()
        })
      })
    }
  }
  SaveResolutionDetails(type: any, name: any, status: any, logs: any) {
    let formdata = new FormData()
    formdata.append('Number', this.dataToTakeAsInput["IncidentNumber"])
    formdata.append('Description', this.dataToTakeAsInput["Description"])
    formdata.append('Type', type)
    formdata.append('Name', name)
    formdata.append('Status', status)
    formdata.append('Logs', logs)
    this.httpClient.post('/api/SaveResolutionDetails', formdata, { responseType: 'text' }).subscribe(data => {
      console.log(data)
    })
  }
  invokeDiagnostic(row: any) {
  }
  getAuditLogs(event) {
    this.showHistory = event.target.checked;
  }
  showLogs(value: any) {
    console.log(value)
    const modalRef = this.modalService.open(LogsComponent, { size: 'lg', backdrop: false });
    let dataPassToChild: any = {};
    dataPassToChild['Logs'] = this.logs;
    (<LogsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  private CheckedWordCloud(e) {
    if (this.wordcloudsample.length == 0) {
      this.httpClient.get('/api/display_resolution/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + this.dataToTakeAsInput['IncidentNumber'] + "/" + 'ticket' + "/" + this.cloudType + "/" + this.RTChosenAlgorithm)
        .subscribe(data => {
          if (data) {
            this.showCloud = true;
            this.tagCloudData = [];
            this.wordcloudsample = data;
            for (var key in this.wordcloudsample) {
              var randomItem = this.myArrayColor[Math.floor(Math.random() * this.myArrayColor.length)];
              this.tagCloudData.push({ text: key + '(' + this.wordcloudsample[key] + ')', weight: (this.wordcloudsample[key]), color: randomItem });
            }
          }
        },
          err => {
            console.log(err);
            throw "";
          });
    }
    this.ShowWordCloud = e.target.checked;
  }
  // -- Attachment analysis --
  private previewImageModal(incidentNumber: string) {
    const modalRef = this.modalService.open(ImagePreviewerComponent, { size: 'lg', backdrop: false });
    let dataPassToChild: any = {};
    dataPassToChild['IncidentNumber'] = incidentNumber;
    (<ImagePreviewerComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  private showOpenTickets(incidentNumber: string, description: string) {
    const modalRef = this.modalService.open(OpenTicketsComponent, { size: 'lg', backdrop: false });
    let dataPassToChild: any = {};
    dataPassToChild['DatasetID'] = 1;
    dataPassToChild['IncidentNumber'] = incidentNumber;
    dataPassToChild['Description'] = description;
    dataPassToChild['openticekts'] = this.openTickets;
    (<OpenTicketsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  step = 0;
  setStep(index: number) {
    this.step = index;
  }
  nextStep() {
    this.step++;
  }
  prevStep() {
    this.step--;
  }
  cloudTypeChanged() {
    this.httpClient.get('/api/display_resolution/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + this.dataToTakeAsInput['IncidentNumber'] + "/" + 'ticket' + "/" + this.cloudType + "/" + this.RTChosenAlgorithm)
      .subscribe(data => {
        if (data) {
          this.tagCloudData = [];
          this.wordcloudsample = data;
          console.log("display word cloud...", data);
          for (var key in this.wordcloudsample) {
            var randomItem = this.myArrayColor[Math.floor(Math.random() * this.myArrayColor.length)];
            this.tagCloudData.push({ text: key + '(' + this.wordcloudsample[key] + ')', weight: (this.wordcloudsample[key] / 20), color: randomItem });
          }
        }
      });
    this.showCloud = true;
  }
  getStatus() {
    this.httpClient.get("/api/getSwitchStatus" + '/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
      let status = data['assignment_enabled']
      if (status == 'true') { this.predAssigneeStatus = true; } else { this.predAssigneeStatus = false; }
    });
  }
  logClicked(e: any) {
    let wordClicked: string;
    this.relatedTickets = this.copyRelatedTickets;
    this.highlitedTickets = [];
    wordClicked = e.text.toString();
    let index = wordClicked.indexOf("(")
    wordClicked = wordClicked.substring(0, index).toLowerCase()
    this.relatedTickets.forEach(ticket => {
      ticket['highlight'] = false;
      if (ticket['close_notes'].toLowerCase().includes(wordClicked)) {
        ticket['highlight'] = true;
        this.highlitedTickets.push(ticket);
      }
    });
    if (this.highlitedTickets.length > 0) {
      this.relatedTickets = [];
      this.relatedTickets = this.highlitedTickets;
    }
  }
  closeAlert() {
    this.scriptStatus = false;
  }
  invokeScriptsPopUp(tabName: string) {
    const modalRef = this.modalService.open(ScriptsPopupComponent, { size: 'lg', backdrop: false });
    let dataPassToChild: any = {};
    dataPassToChild['IncidentNumber'] = this.dataToTakeAsInput['IncidentNumber']
    dataPassToChild['Predicted_Group'] = this.incidentTicketsData[0]['predicted_fields'][0]['assignment_group']
    dataPassToChild['DatasetID'] = 1;
    dataPassToChild['tabName'] = tabName;
    dataPassToChild['Description'] = this.dataToTakeAsInput["Description"];
    (<ScriptsPopupComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  provideArgs(scriptDetails: any) {
    const modalRef = this.modalService.open(ArgsComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
    modalRef.componentInstance.emitData.subscribe(($e) => {
      this.auditLogs = $e;
    })
    let dataPassToChild: any = {};
    dataPassToChild['ScriptDetails'] = scriptDetails;
    dataPassToChild['IncidentNumber'] = this.dataToTakeAsInput['IncidentNumber']
    dataPassToChild['Description'] = this.dataToTakeAsInput["Description"];
    dataPassToChild['Type'] = 'main';
    (<ArgsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  provideRPAArgs(scriptDetails: any) {
    const modalRef = this.modalService.open(RpaPopupComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
    modalRef.componentInstance.emitData.subscribe(($e) => {
      this.auditLogs = $e;
    })
    let dataPassToChild: any = {};
    dataPassToChild['ScriptDetails'] = scriptDetails;
    dataPassToChild['IncidentNumber'] = this.dataToTakeAsInput['IncidentNumber']
    dataPassToChild['Description'] = this.dataToTakeAsInput["Description"];
    dataPassToChild['Type'] = 'RPA';
    (<RpaPopupComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  provide_orchestrator_Args(scriptDetails: any) {
    if (scriptDetails['orchestrator_args_list'] === undefined || scriptDetails['orchestrator_args_list'].length === 0) {
      this.executeWorkflow(scriptDetails)
    } else {
      const modalRef = this.modalService.open(OrchestratorArgsPopupComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
      modalRef.componentInstance.emitData.subscribe(($e) => {
        this.auditLogs = $e;
      })
      let dataPassToChild: any = {};
      dataPassToChild['ScriptDetails'] = scriptDetails;
      dataPassToChild['IncidentNumber'] = this.dataToTakeAsInput['IncidentNumber']
      dataPassToChild['Description'] = this.dataToTakeAsInput["Description"];
      dataPassToChild['Type'] = 'main';
      (<OrchestratorArgsPopupComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
      modalRef.result.then((result) => {
        console.log(result);
      }).catch((result) => {
        console.log(result);
      });
    }
  }
  RPAdiagPopup(row: any) {
    const modalRef = this.modalService.open(RpaDiagPopupComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
    modalRef.componentInstance.emitData.subscribe(($e) => {
      this.auditLogs = $e;
    })
    let dataPassToChild: any = {};
    dataPassToChild['IncidentNumber'] = this.dataToTakeAsInput['IncidentNumber']
    dataPassToChild['Description'] = this.dataToTakeAsInput["Description"];
    dataPassToChild['Row'] = row;
    (<RpaDiagPopupComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  diagPopup(row: any) {
    const modalRef = this.modalService.open(DiagComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
    modalRef.componentInstance.emitData.subscribe(($e) => {
      this.auditLogs = $e;
    })
    let dataPassToChild: any = {};
    dataPassToChild['IncidentNumber'] = this.dataToTakeAsInput['IncidentNumber']
    dataPassToChild['Description'] = this.dataToTakeAsInput["Description"];
    dataPassToChild['Row'] = row;
    (<DiagComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  itemCreated(audits: any) {
    this.auditLogs = audits
  }
  followUp() {
    this.type = 'success';
    this.message = 'Success!! Follow Up Email Drafted Successfully.';
  }
  onOutsideClick(event) {
    if (this.highlitedTickets.length == 0) {
      this.relatedTickets = [];
      if (this.copyRelatedTickets != "No Results Found") {
        this.copyRelatedTickets.forEach(ticket => {
          ticket['highlight'] = false;
        });
      }
      this.relatedTickets = this.copyRelatedTickets;
    }
    else {
      this.highlitedTickets = [];
    }
  }
  openAnnotationModal(incidentNumber: string) {
    const modalRef = this.modalService.open(AnnotationModalComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
    modalRef.componentInstance.ticketNumber = incidentNumber;
  }
  onNavigate() {
    let hostname = "localhost"
    let port = 'enter port number'
    this.httpClient.get('/api/getConfigKey/bpmn_editor').subscribe(data => {
      if (data['Status'] == 'Success') {
        hostname = data['hostname']
        port = data['port']
      }
      window.open('http://' + hostname + ':' + port + '/?name=', "_blank");
    }, err => {
      window.open('http://' + hostname + ':' + port + '/?name=', "_blank");
    });
  }
  executeWorkflow(workflow: any) {
    this.httpClient.get('/api/executeWorkFlow/' + workflow['name'] + '/' + this.dataToTakeAsInput["IncidentNumber"]).subscribe(data => {
      this.SaveResolutionDetails('orchestrator', workflow['name'], 'success', 'Started Successfully.')
      this.httpClient.get('/api/getAuditLogs/' + this.dataToTakeAsInput["IncidentNumber"]).subscribe(data => {
        this.auditLogs = data;
        this.auditLogs.reverse()
        alert('workflow started succesfully');
      });
    }, err => {
      console.error('Could not execute script due to some error! Please try again later');
    });
  }
  clearLogs() {
    this.httpClient.get('api/clearResolutionLogs/' + this.dataToTakeAsInput['IncidentNumber'], { responseType: 'text' }).subscribe(response => {
      this.httpClient.get('/api/getAuditLogs/' + this.dataToTakeAsInput['IncidentNumber']).subscribe(data => {
        this.auditLogs = data;
        this.auditLogs.reverse()
      });
    });
  }
  editScript(script: any, type: any, resolvertype: any) {
    if (resolvertype == "script") {
      let editScript: any
      let args: any = [];
      if (type == 'main') {
        editScript = script
        this.httpClient.get('/api/getArguments/' + 'main' + '/' + editScript).subscribe(data => {
          Object.keys(data).forEach(element => {
            args.push(data[element])
          });
          args = args.toString()
        })
      } else {
        editScript = this.toBeEdittedScript
        this.httpClient.get('/api/getArguments/' + 'diagnostic' + '/' + editScript).subscribe(data => {
          Object.keys(data).forEach(element => {
            args.push(data[element])
          });
          args = args.toString()
        })
      }
      if (editScript.length != 0) {
        this.saveSuccess = false;
        this.httpClient.get('/api/getScriptContent/' + editScript + '/' + type).subscribe(data => {
          if (data != 'Failure') {
            if (data == '') {
              alert("Script is empty")
            } else {
              const modalRef = this.modalService.open(CreateScriptComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
              modalRef.componentInstance.emitData.subscribe(($e) => {
                this.argTypes = $e
              })
              let dataPassToChild: any = {};
              dataPassToChild['Content'] = data;
              dataPassToChild['Args'] = args;
              dataPassToChild['Name'] = editScript;
              dataPassToChild['Type'] = type;
              (<CreateScriptComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
              modalRef.result.then((result) => {
                console.log(result);
              }).catch((result) => {
                console.log(result);
              });
            }
          }
        })
      }
    }
    else if (resolvertype == 'RPA') {
      this.editRPAConfig(resolvertype, script);
    }
    else if (resolvertype == "orchestrator") {
      this.editWorkFlow(script);
    }
  }
  editRPAConfig(type: any, configName: any) {
    let editScript: any;
    let RpaType: any;
    let args: any = [];
    editScript = configName
    RpaType = editScript.split('_')[0];
    if (editScript.length != 0) {
      this.saveSuccess = false;
      this.httpClient.get('/api/getRPAContent/' + editScript + '/' + type).subscribe(data => {
        if (data != 'Failure') {
          if (data == '') {
            alert("Config File is empty")
          } else {
            const modalRef = this.modalService.open(CreateRPAComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
            modalRef.componentInstance.emitData.subscribe(($e) => {
              this.argTypes = $e
            })
            let dataPassToChild: any = {};
            dataPassToChild['Content'] = data;
            dataPassToChild['Name'] = editScript;
            dataPassToChild['RpaType'] = RpaType
            dataPassToChild['Type'] = type;
            (<CreateRPAComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
            modalRef.result.then((result) => {
              console.log(result);
            }).catch((result) => {
              console.log(result);
            });
          }
        }
      })
    }
  }
  editWorkFlow(workflowNme) {
    let hostname = "localhost"
    let port = 'enter port number'
    var wrk = workflowNme;
    this.httpClient.get('/api/getConfigKey/bpmn_editor').subscribe(data => {
      if (data['Status'] == 'Success') {
        hostname = data['hostname']
        port = data['port']
      }
      window.open('http://' + hostname + ':' + port + '/?name=' + wrk);
    }, err => {
      window.open('http://' + hostname + ':' + port + '/?name=' + wrk);
    });
  }
  openGit(loc: any) {
    if (loc == 'store') {
      window.open('');
    } else if (loc == 'rpa') {
      window.open('');
    }
  }
  showAllResourceInfo() {
    let assignment_group;
    for (let field of this.predictedFields)
      if (field == 'group' || field == 'assignment_group') {
        for (let predicted_doc of this.incidentTicketsData[0]['predicted_fields'])
          if (field in predicted_doc) {
            assignment_group = predicted_doc[field];
            break;
          }
        break;
      }
    if (assignment_group) {
      this.httpClient.get('/api/resourceInfoOfGroup/' + assignment_group).subscribe(response => {
        if (response['response'] == 'success') {
          const modalRef = this.modalService.open(ValidationMessageComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
          modalRef.componentInstance.failedRoasterUploadDetails = undefined;
          modalRef.componentInstance.resourcesOfGroupInfo = response['resourceOfGroup'];
          modalRef.componentInstance.assignGroup = assignment_group;
        } else {
          alert('There is no Data Available! Please check DB');
        }
      }, err => {
        console.error('In Method showAllResourceInfo(): ' + err);
      });
    }
  }
  showEntityDetails(entityValue: string) {
    let dataToModal = {};
    this.httpClient.get('/api/ner/getKnowledgeInfo/' + this.dataToTakeAsInput['IncidentNumber'] + '/' + entityValue).subscribe(data => {
      let actualData = data['response'];
      dataToModal['state'] = (typeof (actualData) == 'object') ? true : false;
      if (dataToModal['state']) {
        dataToModal['keys'] = Object.keys(actualData[0]);
        dataToModal['dataToDisplay'] = actualData;
      }
      this.dialog.open(RelatedTicketsModalComponent, {
        data: dataToModal
      });
    }, err => {
      console.error('From Method showEntityDetails(): ' + err);
    });
  }
  private chooseImageDialog() {
    this.activeModal.dismiss('Cross click');
    this.router.navigate(['/screenShotAnalysis']);
  }
}