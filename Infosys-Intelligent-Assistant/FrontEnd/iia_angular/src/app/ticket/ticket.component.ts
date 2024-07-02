/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, AfterViewInit, ViewChild } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { NgbModal, NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ValidationMessageComponent } from '../resource-planning/validation-message/validation-message.component';
import { config } from '../config';
import { RelatedTicketsComponent } from './related-tickets/related-tickets.component';
@Component({
  selector: 'ticket',
  templateUrl: './ticket.component.html',
  styleUrls: ['./ticket.component.css']
})
export class TicketComponent implements OnInit {
  @ViewChild(RelatedTicketsComponent) child1: RelatedTicketsComponent;
  showComparison: boolean = false;
  failure = false;
  err = '';
  approvedFlag = false;
  ticketId: string = "";
  assignmentGroup: string;
  private customerId: number = 1;
  predictedFields: any = [];
  checked: boolean = false;
  exportSuccess: boolean = false;
  rawData: any = [];
  predictedData: any = [];
  predictedTicketsData: any = [];
  allFields: any = [];
  otherFields: any = [];
  selectedAll: any;
  datasetID: number;
  allValues: any = [];
  datasetName: string = "";
  allDatasetNames: any = [];
  predictedApprovedDetails: any = [];
  approveSuccess: boolean = false;
  loading: boolean = false;
  closeResult: string;
  chosenTeam: string;
  selectedTeam: string;
  teams: any = [];
  teamId: number;
  page: number = 1;
  noOfPredictedTickets: number;
  realPredictedTicketsData: any = [];
  itemsPerPage: number;
  loader: boolean;
  switchStatus: boolean;
  priorityList: any = [];
  commentField: string;
  priorityField: string;
  sortField: string;
  sortValue: number = 0;
  filterValueIsList: boolean;
  filterFields: any = [];
  filterField: string;
  filterValues: any = [];
  filterValue: string;
  assignees: any = [];
  prevPredictState: boolean = false;
  accountname: string;
  accountEnable = false;
  showTicketsAssignToMe: boolean = false;
  adminLoginState: boolean = false;
  resourceWorkloads: any = {};
  groupAndResource: any = {};
  ID: number;
  constructor(private httpClient: HttpClient, private httpService: HttpClient, private route: ActivatedRoute, private modalService: NgbModal, private router: Router) {
  }
  ngOnInit() {
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.teams = data['Teams'];
        this.ID = data['DatasetIDs']
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
    this.accountname = config.accountname;
    if (this.accountname.toLocaleLowerCase() == "rb") {
      this.accountEnable = true;
    }
    let datasetPPD = this.route.snapshot.paramMap.get('datasetID');
    let userType = localStorage.getItem('Access')
    if (userType == 'Admin') { this.adminLoginState = true }
    let splitWords;
    splitWords = datasetPPD.split(',');
    this.datasetID = Number(splitWords[0]);
    if (splitWords[1] == 'PPT') {
      this.prevPredictState = true;
    } else if (splitWords[1] == 'ATM') {
      this.showTicketsAssignToMe = true;
    }
    this.httpClient.get('/api/getTeamName/' + this.customerId + "/" + this.datasetID).subscribe(data => {
      this.chosenTeam = data.toString();
      this.httpClient.get('/api/getTeamsWithPredictedData/' + this.customerId).subscribe(data => {
        if (data['Teams'].length > 0) {
          this.teams = data['Teams'];
          this.getPredictedTickets(this.customerId);
        }
      });
    });
  }
  getStatus() {
    this.httpClient.get("/api/getSwitchStatus" + '/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
      let status = data['assignment_enabled']
      if (status == 'true') { this.switchStatus = true; } else { this.switchStatus = false; }
    });
  }
  private getAllFields(custID: number) {
    this.allFields = [];
    this.httpClient.get('/api/getDatasetDetails/' + custID + "/" + this.datasetID).subscribe(data => {
      if (data && data['name'] === "") {
      } else {
        this.datasetName = data['name'];
        let temp = data['fields'];
        temp.forEach((attribute, index) => {
          this.allFields.push(attribute);
        })
        this.commentField = data['comment_field'];
        this.priorityField = data['priority_field'];
        let assignee = this.allFields.find(attribute => attribute === "assigned_to");
        let index_assignee = this.allFields.indexOf(assignee);
        if (index_assignee >= 0)
          this.allFields.splice(index_assignee, 1);
        let ticketNumber = this.allFields.find(attribute => attribute === "number");
        let index_ticketNumber = this.allFields.indexOf(ticketNumber);
        if (index_ticketNumber >= 0)
          this.allFields.splice(index_ticketNumber, 1);
        let priority = this.allFields.find(attribute => attribute === "priority");
        let index_priority = this.allFields.indexOf(priority);
        if (index_priority)
          this.allFields.splice(index_priority, 1);
        this.httpClient.get('/api/allDatasetNames/' + custID).subscribe(data => {
          this.allDatasetNames = data;
        });
        this.getPriorityList(custID)
        this.getPredictedFields(custID);
      }
    });
  }
  private getPriorityList(custID: number) {
    this.priorityList = [];
    //get Predicted Fields list from TblCustomer based on Customer ID
    this.httpClient.get('/api/priorityList/' + custID + "/" + this.datasetID).subscribe(data => {
      this.priorityList = data;
    });
  }
  private getPredictedFields(custID: number) {
    this.predictedFields = [];
    this.otherFields = [];
    this.filterFields = [];
    //get Predicted Fields list from TblCustomer based on Customer ID
    this.httpClient.get('/api/getTeamName/' + this.customerId + "/" + this.datasetID).subscribe(data => {
      this.chosenTeam = data.toString();
      this.httpClient.get('/api/predictedfields/' + custID + "/" + this.chosenTeam).subscribe(data => {
        this.checked = true;
        data['FieldSelections'].forEach((selection) => {
          if (selection['FieldsStatus'] == "Approved") {
            let temp = selection['PredictedFields'];
            temp.forEach((field) => {
              this.predictedFields.push(field.PredictedFieldName);
              this.filterFields.push('predicted_' + field.PredictedFieldName);
            });
            if (this.switchStatus) {
              this.filterFields.push('predicted_assignee');
            }
            this.filterFields.push('number');
            this.filterFields.push('priority');
            this.filterFields = this.filterFields.concat(this.allFields);
          }
        });
        this.predictedFields.forEach(predictedField => {
          let field = this.allFields.find(attribute => attribute === predictedField);
          let index_field = this.allFields.indexOf(field);
          this.allFields.splice(index_field, 1);
          this.otherFields.push(predictedField);
        });
        this.predictedFields.forEach(field => {
          this.httpClient.get('/api/allValues/' + custID + "/" + this.datasetID + "/" + field).subscribe(data => {
            this.allValues[field] = data;
          });
        })
      });
    });
  }
  private teamChange() {
    this.predictedTicketsData = [];
    this.httpClient.get('/api/getTeamID/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
      if (data != 'failure') {
        this.teamId = Number(data);
        this.httpClient.get('/api/getDatasetID/' + this.customerId + '/' + this.teamId).subscribe(data => {
          if (data != '-1') {
            this.datasetID = Number(data);
            this.getPredictedTickets(this.customerId);
          }
        });
      }
    });
  }
  private getPredictedTickets(custID: number) {
    this.httpClient.get('/api/predictedTicketsCount/' + custID + "/" + this.datasetID + '/' + this.prevPredictState).subscribe(data => {
      this.noOfPredictedTickets = data['count'];
      this.itemsPerPage = 10;
      // -- Resource and Workload --
      this.pageChanged();
      this.getAllFields(custID);
      console.log('predicted tickets data is: ' + this.predictedTicketsData);
      this.predictedTicketsData.forEach(ticket => {
        ticket['Selected'] = false;
      });
    });
  }
  pageChanged() {
    this.loader = true;
    this.httpClient.get('/api/calculateResourceWorkload').subscribe(data => {
      if (data['response'] == 'success') {
        this.resourceWorkloads = data['resourceAndWorkload'];
        this.groupAndResource = data['groupAndResource'];
      } else
        console.warn('Could not get data from API! failure response from API');
    }, err => {
      console.error('From pageChanged' + err);
    });
    if ((this.sortField || (this.filterField && this.filterValue)) && !this.showTicketsAssignToMe) {
      this.sortAndFilter();
    } else {
      this.failure = false;
      if (!this.showTicketsAssignToMe) {
        this.httpClient.get('/api/getPredictedTicktesForPage/' + this.customerId + "/" + this.datasetID + '/' + this.itemsPerPage + '/' + this.page + '/' + this.prevPredictState + "/" + this.approvedFlag).subscribe(
          data => {
            this.predictedTicketsData = data;
            if (this.predictedTicketsData.length == 10) {
              this.httpClient.get('/api/predictedTicketsCount/' + this.customerId + "/" + this.datasetID + '/' + this.prevPredictState).subscribe(data => {
                this.noOfPredictedTickets = data['count'];
              });
            }
            if (this.predictedTicketsData.length < 10) {
              this.noOfPredictedTickets = this.page * 10;
            }
            this.loader = false;
            if (this.switchStatus) {
              this.assignees = []
              this.predictedTicketsData.forEach(predictedTicket => {
                this.assignees = this.assignees.concat(predictedTicket['possible_assignees']);
              });
            }
          },
          (error) => {
            let err = error;
            this.failure = true;                          //Error callback
            this.loader = false;
            if (err.error.text == 'no data' && this.page == 1) {
              this.err = "No Records Found";
              this.predictedTicketsData = [];
            } else {
              this.err = err.message;
              if (this.page >= 2) {
                this.page = this.page - 1;
                this.noOfPredictedTickets = this.page * 10;
                this.failure = false;
                this.pageChanged();
              }
            }
          });
      } else {
        this.httpClient.get('/api/ticketsAssignedToUser/' + this.customerId + '/' + this.datasetID + '/' + this.itemsPerPage + '/' + this.page + "/" + this.approvedFlag)
          .subscribe(data => {
            this.predictedTicketsData = data;
            this.predictedTicketsData = data;
            if (this.predictedTicketsData.length == 10) {
              this.httpClient.get('/api/predictedTicketsCount/' + this.customerId + "/" + this.datasetID + '/' + this.prevPredictState).subscribe(data => {
                this.noOfPredictedTickets = data['count'];
              });
            }
            if (this.predictedTicketsData.length < 10) {
              this.noOfPredictedTickets = this.page * 10;
            }
            this.loader = false;
          },
            (error) => {
              let err = error;
              this.failure = true;                          //Error callback
              console.log(err.error.text);
              this.loader = false;
              if (err.error.text == 'no data' && this.page == 1) {
                this.err = "No Records Found";
                this.predictedTicketsData = [];
              } else {
                this.err = err.message;
                if (this.page >= 2) {
                  this.page = this.page - 1;
                  this.noOfPredictedTickets = this.page * 10;
                  this.failure = false;
                  this.pageChanged();
                }
              }                             //Error callback
              this.loader = false;
            });
      }
    }
  }
  private showDetails(ticketID: string, assignmentGroup: string) {
    this.showComparison = true;
    this.ticketId = ticketID;
    this.assignmentGroup = assignmentGroup;
  }
  public exportToCSV() {
    this.httpClient.get('/api/exportPredToCSV/' + this.customerId, { responseType: 'text' }).subscribe(data => {
      this.exportSuccess = true;
      const blob = new Blob([data.toString()], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      let a = document.createElement('a');
      a.href = url;
      a.download = 'PredictedTickets.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
      err => {
        console.log("failed to export to CSV");
        console.log(err);
        throw "";
      });
  }
  private getPredictedDetails() {
    this.httpClient.get('/api/predicted/' + this.ticketId).subscribe(data => {
      this.predictedData = data;
    });
  }
  public getcolor(ticket: any) {
    if (ticket.priority != undefined) {
      if (ticket.priority.includes("1")) {
        var borderproperties = '6px solid #ff0000';
        return borderproperties;
      } else if (ticket.priority.includes("2")) {
        var borderproperties = '6px solid #008000';
        return borderproperties;
      }
    }
  }
  private getRawDetails() {
    this.httpClient.get('/api/tickets/' + this.ticketId).subscribe(data => {
      this.rawData = data;
    });
  }
  public selectAll() {
    this.predictedTicketsData.forEach((ticket, index) => {
      ticket.Selected = this.selectedAll;
    });
  }
  private checkIfAllSelected() {
    this.selectedAll = this.predictedTicketsData.every(function (item: any) {
      return item.Selected == true;
    });
  }
  private datasetChange(ticketNumber: string) {
    this.predictedFields = [];
    this.predictedTicketsData = [];
    this.allValues = [];
    this.httpClient.put('/api/updateRT/' + this.customerId + "/" + ticketNumber + "/" + this.datasetName, null, { responseType: "text" }).subscribe(data => {
      if (data == 'success') {
        this.httpClient.get('/api/predict/' + this.customerId).subscribe(data => {
          this.datasetID = data['DatasetID'];
          this.httpClient.get('/api/predictedTickets/' + this.customerId + "/" + this.datasetID).subscribe(data => {
            this.predictedTicketsData = data;
            this.predictedTicketsData.forEach(ticket => {
              ticket['Selected'] = false;
            });
            this.httpClient.get('/api/predictedfields/' + this.customerId + "/" + this.datasetID).subscribe(data => {
              data['FieldSelections'].forEach((selection) => {
                if (selection['FieldsStatus'] == "Approved") {
                  let temp = selection['PredictedFields'];
                  temp.forEach((field) => {
                    this.predictedFields.push(field.PredictedFieldName);
                  });
                }
              });
              this.predictedFields.forEach(field => {
                this.httpClient.get('/api/allValues/' + this.customerId + "/" + this.datasetID + "/" + field).subscribe(data => {
                  this.allValues[field] = data;
                });
              })
            });
          });
        });
      }
    });
  }
  private predictedFieldValueChange(ticket: string, field: string, value: string) {
    let assignment_group_Field: string = "";
    let number_Field: string = "";
    if (field == 'group') {
      assignment_group_Field = 'group'
      number_Field = 'id';
    }
    else if (field == 'assignment_group') {
      assignment_group_Field = 'assignment_group';
      number_Field = 'number';
    }
    if (field == 'group' || field == 'assignment_group') {
      this.httpClient.get(encodeURI('/api/findpossibleassignees/' + ticket + '/' + encodeURIComponent(value))).subscribe(data => {
        this.predictedTicketsData.forEach(predictedTicket => {
          if (predictedTicket['number'] == ticket) {
            predictedTicket['possible_assignees'] = data['possibleAssignees'];
            predictedTicket['predicted_assigned_to'] = data['predictedAssignedTo'];
          }
        })
      });
    }
  }
  private assignedToChange(ticket: string, value: string) {
  }
  private priorityChange(ticket: string, value: string) {
  }
  public approveTicket() {
    this.loading = true;
    this.approveSuccess = false;
    this.predictedApprovedDetails = {};
    let temp = [];
    let selectedTickets = [];
    this.predictedTicketsData.forEach(predictedTicket => {
      if (predictedTicket.Selected) {
        selectedTickets.push(predictedTicket);
      }
    })
    selectedTickets.forEach(selectedTicket => {
      this.predictedApprovedDetails = {};
      this.predictedApprovedDetails['number'] = selectedTicket['number'];
      if (selectedTicket['predicted_assigned_to'] != undefined) {
        this.predictedApprovedDetails['predicted_assigned_to'] = selectedTicket['predicted_assigned_to'].toString();
      }
      if (selectedTicket['id'] != undefined) {
        this.predictedApprovedDetails['id'] = selectedTicket['id'].toString();
      }
      this.predictedFields.forEach((field, index) => {
        this.predictedApprovedDetails[field] = selectedTicket['predicted_fields'][index][field];
      });
      if (selectedTicket[this.commentField] != undefined) {
        this.predictedApprovedDetails[this.commentField] = selectedTicket[this.commentField];
      }
      if (selectedTicket[this.priorityField] != undefined) {
        this.predictedApprovedDetails[this.priorityField] = selectedTicket[this.priorityField];
      }
      temp.push(this.predictedApprovedDetails);
    });
    this.httpClient.put('/api/updatePredictedDetails/' + this.customerId + "/" + this.datasetID, temp)
      .subscribe(msg => {
        this.loading = false;
        if (msg[0]['Status'] == 'ApprovedTickets') {
          this.loading = false;
          const modalRef = this.modalService.open(ValidationMessageComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
          modalRef.componentInstance.approvedTickets = msg[0]['Approved_Tickets'];
          console.log('Could not approve ticket! it is already approved by another user');
        } else if (msg[0]['Status'] == 'success') {
          this.approveSuccess = true;
        } else if (msg[0]['Status'] == 'partial') {
          const modalRef = this.modalService.open(ValidationMessageComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
          modalRef.componentInstance.approvedTickets = msg[0]['Failed_Tickets'];
        } else {
          alert('Could not approve tickets! please try again later');
          console.log('Could not approve tickets! response from backend is : ' + msg[0]['Status']);
        }
        this.pageChanged();
      },
        err => {
          console.log(err);
          throw "";
          this.loading = false;
        });
  }
  private showRelatedTickets(incidentNumber: string, description: string) {
    const modalRef = this.modalService.open(RelatedTicketsComponent, { size: 'lg', backdrop: false });
    modalRef.componentInstance.emitService.subscribe((emmitedValue) => {
      this.loading = true;
    });
    let dataPassToChild: any = {};
    let rawTicketData: any = []
    dataPassToChild['IncidentNumber'] = incidentNumber;
    dataPassToChild['DatasetID'] = this.datasetID;
    dataPassToChild['Description'] = description;
    dataPassToChild['PredictRadio'] = "realTime";
    this.otherFields.forEach(rawpredictedField => {
      var obj = {};
      obj[rawpredictedField] = this.predictedTicketsData.find(attribute => attribute.number === incidentNumber)[rawpredictedField];
      rawTicketData.push(obj);
    });
    dataPassToChild['rawTicketData'] = rawTicketData;
    (<RelatedTicketsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      this.loading = result['ApproveLoading'];
      const currentRoute = this.router.url;
      if (this.loading == false) {
        this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
          this.router.navigate([currentRoute]); // navigate to same route
        });
      }
    });
  }
  saveUserComment(event, number) {
    let userComment = event.target.outerText;
    if (userComment) {
      this.predictedTicketsData.forEach(predictedTicket => {
        if (predictedTicket.number == number) {
          predictedTicket[this.commentField] = userComment;
        }
      });
    }
  }
  sort(fieldName) {
    if (this.sortField == fieldName) {
      this.sortValue = (this.sortValue == 1) ? -1 : 1;
    } else {
      this.sortField = fieldName;
      this.sortValue = 1;
    }
    if (this.sortField == 'number') {
      if (this.predictedTicketsData[0]['number'] == undefined) {
        this.sortField = 'id';
      }
    }
    this.sortAndFilter();
  }
  filterFieldChange() {
    if (this.filterField == 'assignment_group' || this.filterField == 'predicted_assignment_group') {
      this.filterValues = this.allValues['assignment_group'];
      this.filterValueIsList = true;
    } else if (this.filterField == 'predicted_assignee') {
      this.filterValues = this.assignees;
      this.filterValueIsList = true;
    } else {
      this.filterValueIsList = false;
    }
  }
  sortAndFilter() {
    if (this.sortField || (this.filterField && this.filterValue)) {
      if (this.sortField == undefined) {
        this.sortField = this.filterField;
        this.sortValue = 1;
      }
      this.httpClient.get('/api/sortAndFilter/' + this.customerId + '/' + this.datasetID + '/' + this.filterField + '/' + this.filterValue + '/' + this.sortField + '/' + this.sortValue + '/' + this.itemsPerPage + '/' + this.page + '/' + this.prevPredictState + '/' + this.approvedFlag)
        .subscribe(data => {
          if (data != 'failure') {
            if (data[1]) {
              this.noOfPredictedTickets = data[1];
            }
            this.predictedTicketsData = data[0];
          }
          this.loader = false;
        }, err => {
          console.error('Could not recieve sorted ticket/filtered detials! Please try again later');
        });
    } else {
      console.log('value missing in sortAndFilter method');
    }
  }
  resetFilter() {
    this.filterField = undefined;
    this.filterValue = undefined;
    this.getPredictedTickets(this.customerId);
  }
  showAllResourceInfo(predictedFields: any) {
    let assignment_group;
    this.loading = true;
    for (let field of this.predictedFields) {
      if (field == 'group' || field == 'assignment_group') {
        for (let predictFieldDoc of predictedFields)
          if (field in predictFieldDoc) {
            assignment_group = predictFieldDoc[field];
            break;
          }
        break;
      }
    }
    if (assignment_group) {
      this.httpClient.get('/api/resourceInfoOfGroup/' + assignment_group).subscribe(response => {
        this.loading = false;
        if (response['response'] == 'success') {
          const modalRef = this.modalService.open(ValidationMessageComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
          modalRef.componentInstance.failedRoasterUploadDetails = undefined;
          modalRef.componentInstance.resourcesOfGroupInfo = response['resourceOfGroup'];
          modalRef.componentInstance.assignGroup = assignment_group;
        } else {
          console.warn('In Method showAllResourceInfo(): Failure Response from API');
          alert('There is no Data Available! Please check DB');
        }
      }, err => {
        console.error('In Method showAllResourceInfo(): ' + err);
      });
    }
  }
}
