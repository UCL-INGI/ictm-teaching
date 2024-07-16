/**
 import Handsontable from 'handsontable';
 import {TextEditor} from "handsontable/editors";
 **/

//import {TextEditor} from "./textEditor";

fetch('/assignment/load_data')
    .then(response => response.json())
    .then(loadData => {
        console.log(loadData);

        const {courses, users, teachers, researchers, preferences, organizations, current_year} = loadData;
        const example = document.getElementById("handsontable");

        courses.map(course => {
            let teachersId = teachers.filter(teacher => teacher.course_id === course.id && teacher.course_year === current_year);
            let teachersName = teachersId.map(teacher => {
                let teacherUser = users.find(user => user.id === teacher.user_id);
                return teacherUser ? teacherUser.name + " " + teacherUser.first_name : '';
            });
            course.assigned_teachers = teachersName.join(', ');
        });

        const fixedHeaders = [
            "Fgs",
            "Researchers",
            "Org",
            "Promoter",
            "Total Load",
            "Load Q1",
            "Load Q2",
        ];

        const fixedRowsText = [
            "Id",
            "Quadri",
            "Acads",
            "Nbr Student 22/23",
            "Assistant",
            "Total for now",
        ];

        const lenFixedRowsText = fixedRowsText.length
        const lenFixedHeaders = fixedHeaders.length

        //Split long text in the course header
        const coursesHeaders = courses.map(course => {
            const maxLength = 30;
            const courseName = course.title;

            if (courseName.length > maxLength) {
                const firstLine = courseName.substring(0, maxLength / 2);
                const secondLine = courseName.substring(maxLength / 2);
                const finalResult = `${secondLine}<br>${firstLine}<br>${course.code}`;
                return finalResult
            } else {
                const finalResult = `${courseName}<br>${course.code}`;
                return finalResult;
            }
        });

        //Create all course header
        const allHeaders = fixedHeaders.concat(coursesHeaders);

        function fixedRowsData() {
            let rows = [];
            const properties = ['id', 'quadri', 'assigned_teachers', 'nbr_students', 'nbr_teaching_assistants', 'tutors'];
            for (let i = 0; i < lenFixedRowsText; i++) {
                let row = {};
                row.researchers = {};
                row.researchers.fgs = "";
                row.researchers.name = "";
                //row.researchers.name = fixedRowsText[i];
                row.org = "";
                row.charge1 = "";
                row.charge2 = "";
                row.charge3 = "";
                row.check = "";

                courses.forEach(course => {
                    row[course.code] = properties[i] !== 'tutors' ? course[properties[i]] : 0;
                });
                rows.push(row);
            }
            return rows;
        }

        function buildRow(user, isFilled) {
            const row = {};
            row.researchers = {
                fgs: user.id,
                name: isFilled ? `${user.name} ${user.first_name}` : ""
            };
            return row;
        }

        function userRowsData() {
            const rows = [];
            const researcherUsers = users.filter(user => user.is_researcher === true);

            researcherUsers.forEach(user => {
                const row = buildRow(user, true);
                const emptyRow = buildRow(user, false);

                const matchingAssistant = researchers.find(researcher => researcher.user_id === user.id);
                const assistantOrg = organizations.find(org => org.id === user.organization_id);

                row.org = assistantOrg ? assistantOrg.name : "";
                row.charge1 = matchingAssistant ? (users.find(sup => sup.id === user.supervisor_id)?.name ?? "") : "";
                row.charge2 = matchingAssistant ? matchingAssistant.max_loads : 0;
                row.charge3 = 0;
                row.check = 0;

                emptyRow.org = "";
                emptyRow.charge1 = "";
                emptyRow.charge2 = "";
                emptyRow.charge3 = "";
                emptyRow.check = "";

                const researcher = researchers.find(researcher => researcher.user_id === user.id);
                const userPrefs = preferences.filter(pref => pref.researcher_id === researcher.id && pref.course_year === current_year);

                let pos = 1;
                courses.forEach(course => {
                    const isPref = userPrefs.find(pref => pref.course_id === course.id && pref.course_year === current_year);
                    const code = course.code;
                    row[code] = isPref ? pos++ : "";
                    emptyRow[code] = "";
                });

                rows.push(row);
                rows.push(emptyRow);
            });

            return rows;
        }

        const fixedRows = fixedRowsData();
        const userRows = userRowsData();

        function getCourseColumns() {
            const fixedColumns = [
                {data: 'researchers.fgs'},
                {data: 'researchers.name'},
                {data: 'org'},
                {data: 'charge1'},
                {data: 'charge2'},
                {data: 'charge3'},
                {data: 'check'}
                /*{
                  type: 'dropdown',
                  source: userNames,
                  filter: true
                }*/
            ];

            courses.forEach(course => {
                const code = course.code;
                let col = {data: code}
                fixedColumns.push(col)
            });
            return fixedColumns;
        }

        const columns = getCourseColumns();

        let data = fixedRows.concat(userRows);
        const nbrLines = data.length - 1;
        const nbrCols = columns.length - 1;

        const startRow = lenFixedRowsText;
        const startCol = 1;
        const endRow = nbrLines;
        const endCol = lenFixedHeaders - 1;

        const mergeCellsSettings = generateMergeCellSettings(startRow, startCol, endRow, endCol);

        function generateMergeCellSettings(startRow, startCol, endRow, endCol) {
            const mergeCellsSettings = [];
            for (let row = startRow; row < endRow; row += 2) {
                for (let col = startCol; col <= endCol; col++) {
                    mergeCellsSettings.push({
                        row: row,
                        col: col,
                        rowspan: 2,
                        colspan: 1
                    });
                }
            }

            return mergeCellsSettings;
        }

        function storeDataLocally(data) {
            localStorage.setItem('table', JSON.stringify(data));
        }

        function storeCellsMeta(cellsMeta) {
            localStorage.setItem('cellsMeta', JSON.stringify(cellsMeta));
        }

        function retrieveDataLocally() {
            const storedData = localStorage.getItem('table');
            if (storedData) {
                data = JSON.parse(storedData);
            }
        }

        function retrieveCellsMetaLocally() {
            //localStorage.removeItem('cellsMeta');
            const cellsMeta = localStorage.getItem('cellsMeta');
            return cellsMeta ? JSON.parse(cellsMeta) : null;
        }

        function resetDataLocally() {
            localStorage.clear();
        }

        // Verify if the table is modified locally
        retrieveDataLocally();
        let comments = retrieveCellsMetaLocally();
        let isCollectedMetaData = true;

        const table = new Handsontable(example, {
            data: data,
            //editor: TextEditor,
            fixedColumnsLeft: lenFixedHeaders,
            fixedRowsTop: lenFixedRowsText,
            manualColumnMove: true,
            manualColumnResize: true,
            manualRowResize: true,
            mergeCells: mergeCellsSettings,
            comments: true,
            hiddenColumns: {
                columns: [0],
                indicators: true,
            },
            hiddenRows: {
                rows: [0],
                indicators: true,
            },
            contextMenu: ['commentsAddEdit', 'commentsRemove', 'hidden_columns_hide', 'hidden_rows_hide', 'hidden_columns_show', 'hidden_rows_show'],
            filters: true,
            dropdownMenu: ['filter_by_value', 'filter_action_bar'],
            className: 'controlsQuickFilter htCenter htMiddle',
            colHeaders: allHeaders,
            //className: 'htCenter htMiddle',
            columns: columns,
            colWidths: 100,
            columnHeaderHeight: 225,
            rowHeaders: fixedRowsText,
            rowHeaderWidth: 125,
            init: function () {
                if (comments) {
                    comments.forEach(comment => {
                        this.setCellMeta(comment.row, comment.col, comment.key, comment.value);
                    });
                }
                isCollectedMetaData = false;
            },
            afterGetColHeader: function (col, th) {
                th.style.transform = 'rotate(180deg)';
                th.style.writingMode = 'vertical-lr';
                th.style.textAlign = 'center';
                th.style.fontWeight = 'bold';
                th.style.height = '100px';
                th.style.lineHeight = '100px';

                if (col > lenFixedHeaders - 1) {
                    let colData = this.getDataAtCol(col);
                    if (colData[5] >= colData[4]) {
                        th.style.backgroundColor = 'green';
                    }
                }
            },
            afterChange: function (changes) {
                if (changes) {
                    changes.forEach(([row, prop, oldValue, newValue]) => {
                        let col = this.propToCol(prop);
                        if ((col >= lenFixedHeaders && row >= lenFixedRowsText) && (row % 2 === 1)) {
                            //Boolean to determine whether a cell is updated or empty
                            let isDeleted = false;

                            //Update total course assistants
                            if (oldValue !== null && newValue === null) {
                                isDeleted = true;
                            }

                            const colInfos = this.getDataAtProp(prop);
                            let nbrAssistants = colInfos[5];

                            if (isDeleted) {
                                nbrAssistants--;
                            } else {
                                nbrAssistants++;
                            }
                            this.setDataAtCell(5, col, nbrAssistants);

                            //Update user load
                            const rowInfos = this.getDataAtRow(row - 1);
                            const quadri = colInfos[1];
                            if (quadri === 1) {
                                let load_q1 = rowInfos[5];
                                if (isDeleted) {
                                    load_q1--;
                                } else {
                                    load_q1++;
                                }
                                this.setDataAtCell(row - 1, 5, load_q1);
                            } else {
                                let load_q2 = rowInfos[6];
                                if (isDeleted) {
                                    load_q2--;
                                } else {
                                    load_q2++;
                                }
                                this.setDataAtCell(row - 1, 6, load_q2);
                            }
                        }
                    });
                    //storeDataLocally(data);
                }
            },
            afterSetCellMeta: function (row, col, key, value) {
                if (key === 'comment' && !isCollectedMetaData) {
                    let comments = JSON.parse(localStorage.getItem('cellsMeta')) || [];
                    const comment = {'row': row, 'col': col, 'key': key, 'value': value}
                    comments.push(comment);
                    storeCellsMeta(comments);
                }
            },
            afterRenderer: function (TD, row, col, prop, value, cellProperties) {
                if ((col >= lenFixedHeaders && row >= lenFixedRowsText) && (row % 2 === 1) && (value !== '')) {
                    TD.style.fontWeight = 'bold'; // Bold text
                    TD.style.textAlign = 'left'; // Left alignment
                }
                //Style first col if needed
                if (col === 0 && row < lenFixedRowsText) {
                    TD.style.fontWeight = 'bold';
                    TD.style.textAlign = 'left';
                }
                //(row%2) === 1 to avoid empty lines
                if (row >= lenFixedRowsText && (row % 2) === 0 && col < lenFixedHeaders) {
                    const rowValue = this.getDataAtRow(row);
                    if (col === 5 || col === 6) {
                        const total_load = rowValue[4];
                        const load_q1 = rowValue[5];
                        const load_q2 = rowValue[6];

                        //First case: load Q1 + Q2 = total load
                        //Second case: load Q1 or Q2 = half of total load
                        if (load_q1 + load_q2 > total_load) {
                            TD.style.backgroundColor = 'red';
                        } else if ((total_load === 4 || total_load === 2) && (total_load / value <= 2 || load_q1 + load_q2 === total_load)) {
                            TD.style.backgroundColor = 'green';
                        } else if (total_load === 1) {
                            if (value === 1) {
                                TD.style.backgroundColor = 'green';
                            } else {
                                if ((load_q1 === 1 && load_q2 === 0) || (load_q1 === 0 && load_q2 === 1)) {
                                    TD.style.backgroundColor = 'green';
                                }
                            }
                        }
                    }
                }
            },
            customBorders: [
                {
                    range: {
                        from: {
                            row: 0,
                            col: 0,
                        },
                        to: {
                            row: nbrLines,
                            col: 6,
                        },
                    },
                    end: {
                        width: 2,
                        color: 'black'
                    },
                },
                {
                    range: {
                        from: {
                            row: 0,
                            col: 0,
                        },
                        to: {
                            row: 5,
                            col: nbrCols,
                        },
                    },
                    bottom: {
                        width: 2,
                        color: 'black'
                    },
                },
                {
                    row: 5,
                    col: 6,
                    bottom: {
                        width: 2,
                        color: 'black'
                    }
                },
            ],
            beforeFilter(conditionsStack) {
                const filtersPlugin = this.getPlugin('filters');
                const tab = this.getData();

                let values = [];
                const filteredResults = [];
                const col = conditionsStack[0].column;

                if (conditionsStack && conditionsStack.length > 0) {
                    for (let i = 0; i < conditionsStack.length; i++) {
                        values = conditionsStack[i].conditions[0].args.flat();

                        for (const row of tab) {
                            if (values.includes(row[col])) {
                                filteredResults.push(row[0]);
                            }
                        }
                    }
                }
                filtersPlugin.clearConditions();
                filtersPlugin.addCondition(0, 'by_value', [filteredResults]);
            },
            afterFilter(conditionsStack) {
                const filtersPlugin = this.getPlugin('filters');
                const filtersRowsMap = filtersPlugin.filtersRowsMap;

                // Exclude fixed lines from the filter
                for (let i = 0; i < lenFixedRowsText; i++) {
                    filtersRowsMap.setValueAtIndex(i, false);
                }
            },
            licenseKey: "non-commercial-and-evaluation",
        });

        $(document).ready(function () {
            $('#button-export').click(exportToCSV);
            $('#button-create-assignments').click(saveAssignments);
            $('#button-clear-assignments').click(clearAssignments)
            $('#button-publish-assignments').click(publishAssignments);
        });

        function exportToCSV() {
            console.log('Export to CSV clicked');
        }

        function saveAssignments() {
            storeDataLocally(data);
        }

        function clearAssignments() {
            resetDataLocally();
        }

        async function publishAssignments() {
            const slicedData = data.slice(lenFixedRowsText);
            const result = [];

            for (let i = 1; i < slicedData.length - 1; i += 2) {
                const row = slicedData[i];
                let temp_result = Object.keys(row).reduce((filteredRow, key) => {
                    if (row[key] !== null && row[key] !== "") {
                        filteredRow[key] = row[key];
                    }
                    return filteredRow;
                }, {});
                result.push(temp_result);
            }

            try {
                const response = await fetch('/assignment/publish_assignments', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(result),
                });

                if (response.ok) {
                    const responseData = await response.json();
                    console.log('Success:', responseData);
                } else {
                    console.error('Failed to publish assignments:', response.statusText);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });

