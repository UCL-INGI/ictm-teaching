import {
    fixedHeaders,
    fixedRowsText,
    ColumnIndices,
    RowIndices,
    lenFixedRowsText,
    lenFixedHeaders,
    borderStyle,
    requiredProperties,
} from './constants.js';

fetch('/assignment/load_data')
    .then(response => response.json())
    .then(loadData => {
        const {
            courses,
            users,
            teachers,
            researchers,
            supervisors,
            preferences,
            organizations,
            current_year,
            saved_data,
            MAX_LOAD
        } = loadData;

        courses.forEach(course => {
            let teachersId = Object.values(teachers).filter(teacher => teacher.course_id === course.id);
            let teachersName = teachersId.map(teacher => {
                let teacherUser = users[teacher.user_id];
                return teacherUser ? `${teacherUser.name} ${teacherUser.first_name}` : '';
            });
            course.assigned_teachers = teachersName.join(', ');
        });

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

        function fixedRowsData(clearData = false) {
            let rows = [];

            const allProperties = Object.keys(courses[0]);
            const properties = allProperties.filter(prop => requiredProperties.includes(prop));
            // Use to keep the order of the properties
            const orderedProperties = requiredProperties.map(prop => properties.includes(prop) ? prop : null).filter(prop => prop !== null);
            orderedProperties.push('total_assistants')

            for (let i = 0; i < lenFixedRowsText; i++) {
                let row = {
                    researchers: {
                        id: "",
                        name: ""
                    },
                    org: "",
                    promoter: "",
                    totalLoad: "",
                    loadQ1: "",
                    loadQ2: ""
                };

                courses.forEach(course => {
                    // Check if the current property is 'total_assistants'
                    // If 'clearData' is true, set 'total_assistants' to 0
                    // Otherwise, calculate based on 'saved_data' if available, or set to 0 if not
                    row[course.id] = (orderedProperties[i] === 'total_assistants')
                        ? (clearData ? 0 : (saved_data ? saved_data.filter(assignment => assignment.course_id === course.id).length : 0))
                        : course[orderedProperties[i]]; // For other properties, assign the value from the course data.
                });
                rows.push(row);
            }
            return rows;
        }

        function buildRow(researcher, user, isFilled) {
            const row = {};
            row.researchers = {
                id: researcher.id,
                name: isFilled ? `${user.name} ${user.first_name}` : ""
            };
            return row;
        }

        function userRowsData(clearData = false) {
            const rows = [];

            for (const researcherId in researchers) {
                const researcher = researchers[researcherId];
                const user = users[researcher.user_id];
                //The first line displays the preferences for each user
                const preferenceRow = buildRow(researcher, user, true);
                //The second line allows admins to assign a course to the user
                const assignmentRow = buildRow(researcher, user, false);
                const assistantOrg = organizations[user.organization_id];

                let researcherSupervisor = Object.values(supervisors).filter(supervisor => supervisor.researcher_id === researcher.id);
                let supervisorNames = researcherSupervisor.map(supervisor => {
                    let user = users[supervisor.supervisor_id];
                    return user ? `${user.name} ${user.first_name}` : '';
                });
                researcher.promoters = supervisorNames.join(', ');
                preferenceRow.org = assistantOrg ? assistantOrg.name : "";
                preferenceRow.promoter = researcher.promoters;
                preferenceRow.totalLoad = researcher.max_loads;

                const foundData = saved_data && saved_data.find(data => data.researcher_id === researcher.id);
                preferenceRow.loadQ1 = foundData && !clearData ? foundData.load_q1 : 0;
                preferenceRow.loadQ2 = foundData && !clearData ? foundData.load_q2 : 0;

                //This line is only used to store course assignments, so the other values are empty.
                const emptyKeys = ['org', 'promoter', 'totalLoad', 'loadQ1', 'loadQ2'];
                emptyKeys.forEach(key => {
                    assignmentRow[key] = "";
                });

                const userPrefs = Object.values(preferences).filter(pref => pref.researcher_id === researcher.id);

                courses.forEach(course => {
                    const existingPref = userPrefs.find(pref => pref.course_id === course.id);
                    const savedAssignment = saved_data && !clearData ? saved_data.find(data => data.researcher_id === researcher.id && data.course_id === course.id) : null;
                    preferenceRow[course.id] = existingPref ? existingPref.rank : "";
                    assignmentRow[course.id] = savedAssignment ? savedAssignment.position : "";
                });
                rows.push(preferenceRow);
                rows.push(assignmentRow);
            }
            return rows;
        }

        const fixedRows = fixedRowsData();
        const userRows = userRowsData();

        function getCourseColumns() {
            const fixedColumns = [
                {data: 'researchers.id'},
                {data: 'researchers.name'},
                {data: 'org'},
                {data: 'promoter'},
                {data: 'totalLoad'},
                {data: 'loadQ1'},
                {data: 'loadQ2'}
            ];

            courses.forEach(course => {
                const code = course.id;
                let col = {data: code};
                fixedColumns.push(col)
            });
            return fixedColumns;
        }

        const columns = getCourseColumns();

        let data = fixedRows.concat(userRows);

        const nbrLines = data.length - 1;
        const nbrCols = columns.length - 1;

        const mergeCellsSettings = [];
        for (let row = lenFixedRowsText; row < nbrLines; row += 2) {
            for (let col = 1; col <= lenFixedHeaders - 1; col++) {
                mergeCellsSettings.push({
                    row: row,
                    col: col,
                    rowspan: 2,
                    colspan: 1
                });
            }
        }

        const table = new Handsontable(document.getElementById("handsontable"), {
            data: data,
            fixedColumnsLeft: lenFixedHeaders,
            fixedRowsTop: lenFixedRowsText,
            manualColumnMove: true,
            manualColumnResize: true,
            manualRowResize: true,
            mergeCells: mergeCellsSettings,
            hiddenColumns: {
                columns: [0],
                indicators: true,
            },
            hiddenRows: {
                rows: [0],
                indicators: true,
            },
            contextMenu: ['commentsAddEdit', 'commentsRemove', 'hidden_columns_hide', 'hidden_rows_hide', 'hidden_columns_show', 'hidden_rows_show'],
            comments: true,
            filters: true,
            dropdownMenu: ['filter_by_value', 'filter_action_bar', 'undo'],
            className: 'controlsQuickFilter htCenter htMiddle',
            colHeaders: allHeaders,
            columns: columns,
            colWidths: 100,
            columnHeaderHeight: 225,
            rowHeaders: fixedRowsText,
            rowHeaderWidth: 125,
            // Disable the cells that contain user preferences
            cells: function (row, col) {
                const cellProperties = {};
                if (row >= lenFixedRowsText && col >= lenFixedHeaders && row % 2 === 0) {
                    cellProperties.readOnly = true;
                }
                return cellProperties;
            },
            afterInit: function () {
                const sourceData = this.getSourceData();
                saved_data.forEach(assignment => {
                    const rowIndex = sourceData.findIndex(row => row.researchers.id === assignment.researcher_id);

                    if (rowIndex !== -1) {
                        const colIndex = this.propToCol(assignment.course_id);

                        const commentsPlugin = this.getPlugin('comments');
                        //Id is set for the two merged rows, and we want to set the comment for the assignment row
                        commentsPlugin.setCommentAtCell(rowIndex + 1, colIndex, assignment.comment);
                    }
                });
            },
            afterGetColHeader: function (col, th) {
                th.style.transform = 'rotate(180deg)';
                th.style.writingMode = 'vertical-lr';
                th.style.textAlign = 'center';
                th.style.fontWeight = 'bold';
                th.style.height = '100px';
                th.style.lineHeight = '100px';

                let colData = this.getDataAtCol(col);
                if (col > lenFixedHeaders - 1) {
                    if (colData[RowIndices.ASSISTANTS] === 0) {
                        th.style.backgroundColor = '#E1BEE7';
                    } else if (colData[RowIndices.TOTAL_ASSISTANT_NOW] >= colData[RowIndices.ASSISTANTS]) {
                        th.style.backgroundColor = colData[RowIndices.TOTAL_ASSISTANT_NOW] === colData[RowIndices.ASSISTANTS] ? 'green' : 'red';
                    }
                }
            },
            afterChange: function (changes) {
                if (changes) {
                    changes.forEach(([row, prop, oldValue, newValue]) => {
                        let col = this.propToCol(prop);

                        if ((col >= lenFixedHeaders && row >= lenFixedRowsText) && (row % 2 === 1)) {
                            const colInfos = this.getDataAtProp(prop);
                            const quadri = colInfos[RowIndices.QUADRI];
                            let loadKey = quadri === 1 ? ColumnIndices.LOAD_Q1 : ColumnIndices.LOAD_Q2;

                            //Count the number of assignments to determine the value of loads
                            let researcherRow = this.getDataAtRow(row).slice(lenFixedHeaders);
                            let loadValue = researcherRow.filter((value, index) => {
                                //Check if the course is in the same quadri
                                const courseQuadri = this.getDataAtCell(RowIndices.QUADRI, index + lenFixedHeaders);
                                return value !== null && value !== '' && courseQuadri === quadri;
                            }).length;
                            this.setDataAtCell(row - 1, loadKey, loadValue);

                            //Count the number of assignments to determine the number of assistants
                            let courseCol = this.getDataAtCol(col).slice(lenFixedRowsText);
                            let nbrAssistants = courseCol.filter((value, index) => index % 2 === 1 && value !== null && value !== '').length;
                            this.setDataAtCell(RowIndices.TOTAL_ASSISTANT_NOW, col, nbrAssistants);
                        }
                    });
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
                    if (col === ColumnIndices.LOAD_Q1 || col === ColumnIndices.LOAD_Q2) {
                        const total_load = rowValue[ColumnIndices.TOTAL_LOAD];
                        const load_q1 = rowValue[ColumnIndices.LOAD_Q1];
                        const load_q2 = rowValue[ColumnIndices.LOAD_Q2];

                        //First case: load Q1 + Q2 = total load
                        //Second case: load Q1 or Q2 = half of total load
                        if (load_q1 + load_q2 > total_load) {
                            TD.style.backgroundColor = 'red';
                        } else if ((total_load === MAX_LOAD['Teaching assistant'] || total_load === MAX_LOAD["Phd"]) && (total_load / value <= MAX_LOAD["Phd"] || load_q1 + load_q2 === total_load)) {
                            TD.style.backgroundColor = 'green';
                        } else if (total_load === MAX_LOAD["Postdoc"]) {
                            if (value === MAX_LOAD["Postdoc"]) {
                                TD.style.backgroundColor = 'green';
                            } else {
                                if ((load_q1 === MAX_LOAD["Postdoc"] && load_q2 === 0) || (load_q1 === 0 && load_q2 === MAX_LOAD["Postdoc"])) {
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
                        from: {row: 0, col: 0},
                        to: {row: nbrLines, col: 6}
                    },
                    end: borderStyle,
                },
                {
                    range: {
                        from: {row: 0, col: 0},
                        to: {row: 5, col: nbrCols}
                    },
                    bottom: borderStyle,
                },
                {
                    row: 5,
                    col: 6,
                    bottom: borderStyle
                },
            ],
            beforeFilter(conditionsStack) {
                const filtersPlugin = this.getPlugin('filters');
                //Get the user data without the fixed rows
                const tab = this.getData().slice(lenFixedRowsText);

                let values = [];
                const filteredResults = [];
                //Get the number of the column to filter

                if (conditionsStack && conditionsStack.length > 0) {
                    const col = conditionsStack[0].column;

                    if (conditionsStack && conditionsStack.length > 0) {
                        for (let i = 0; i < conditionsStack.length; i++) {
                            //Get the matching values to filter
                            values = conditionsStack[i].conditions[0].args.flat();

                            //Verify if the row value for the specific column is in the filter
                            for (const row of tab) {
                                if (values.includes(row[col])) {
                                    //Push id to the filteredResults array
                                    filteredResults.push(row[0]);
                                }
                            }
                        }
                    }
                    filtersPlugin.clearConditions();
                    //Create a new condition to filter the data based on the id
                    filtersPlugin.addCondition(0, 'by_value', [filteredResults]);
                }
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
            let toastNotification = new bootstrap.Toast(document.getElementById('toast-notification'));

            $('#button-export').click(function () {
                const exportPlugin = table.getPlugin('exportFile');
                exportPlugin.downloadFile('csv', {
                    bom: false,
                    columnDelimiter: ',',
                    columnHeaders: true,
                    exportHiddenColumns: false,
                    exportHiddenRows: false,
                    fileExtension: 'csv',
                    filename: 'ICTM-CSV-file_[YYYY]-[MM]-[DD]',
                    mimeType: 'text/csv',
                    rowDelimiter: '\r\n',
                    rowHeaders: true
                });
                updateToastContent('Data exported to CSV');
                toastNotification.show();
            });

            async function saveAssignment(isDraft = false) {
                const slicedData = data.slice(lenFixedRowsText);
                const savedData = [];
                const commentsPlugin = table.getPlugin('comments');

                for (let i = 0; i < slicedData.length; i += 2) {
                    const preferenceRow = slicedData[i];
                    const assignmentRow = slicedData[i + 1];

                    const userData = {
                        researcher_id: preferenceRow.researchers.id,
                        load_q1: preferenceRow.loadQ1,
                        load_q2: preferenceRow.loadQ2,
                        comment: preferenceRow.comment
                    };

                    const courseData = {};
                    courses.forEach(course => {
                        const col = table.propToCol(course.id);
                        const comment = commentsPlugin.getCommentAtCell(i + lenFixedRowsText + 1, col);
                        if (assignmentRow[course.id] !== '' && assignmentRow[course.id] !== null) {
                            courseData[course.id] = {
                                position: assignmentRow[course.id],
                                comment: comment
                            };
                        }
                    });

                    const comments = {
                        preference: preferenceRow.comment,
                        assignment: assignmentRow.comment,
                    };

                    savedData.push({userData, courseData, comments});
                }

                const tableData = {
                    data: savedData,
                    isDraft: isDraft
                };

                try {
                    const response = await fetch('/assignment/publish_assignments', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(tableData),
                    });

                    if (response.ok) {
                        let msg = isDraft ? 'Draft saved' : 'Assignments published';
                        updateToastContent(msg);
                        toastNotification.show();
                    } else {
                        const errorData = await response.json();
                        const errorMessage = errorData.error || 'Failed to publish assignments';

                        updateToastContent(errorMessage);
                        toastNotification.show();
                    }
                } catch (error) {
                    updateToastContent('Error: ' + error);
                    toastNotification.show();
                }
            }

            $('#button-create-assignments').click(async function () {
                await saveAssignment(true);
            });

            $('#button-clear-assignments').click(function () {
                const newFixedRows = fixedRowsData(true);
                const newUsersRow = userRowsData(true);
                data = newFixedRows.concat(newUsersRow);

                table.loadData(data);
                updateToastContent('Data cleared');
                toastNotification.show();
            });

            $('#button-publish-assignments').click(async function () {
                await saveAssignment();
            });
        });
    });

