import QtQuick 2.0
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.2

ApplicationWindow {
    id: window
    title: "PyParadox"
    width: 900
    height: 600
    visible: true

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Qt.platform.os === "osx" ? 16 : 6

        Image {
            id: logo
            source: imagePath

            anchors.horizontalCenter: parent.horizontalCenter
        }

        RowLayout {
            ColumnLayout {
                Label {
                    text: "Mods:"
                }
                PluginListView {
                    id: modsView
                    model: modsModel

                    Layout.fillHeight: true
                    Layout.fillWidth: true
                }
            }
            ColumnLayout {
                Label {
                    text: "DLCs:"
                }
                PluginListView {
                    id: dlcsView
                    model: dlcsModel

                    Layout.fillHeight: true
                    Layout.fillWidth: true
                }
            }
            ColumnLayout {
                Label {
                    text: "Expansions:"
                }
                PluginListView {
                    id: expansionsView
                    model: expansionsModel

                    Layout.fillHeight: true
                    Layout.fillWidth: true
                }
            }
            Component.onCompleted: logicWrapper.resetModels()
        }

        RowLayout {
            Item {
                Layout.fillWidth: true
            }
            Button {
                id: configBtn
                KeyNavigation.tab: runBtn
                KeyNavigation.right: runBtn

                activeFocusOnPress: true

                text: "Configure"
                onClicked: configDialog.open()
            }
            Button {
                id: runBtn
                KeyNavigation.backtab: configBtn
                KeyNavigation.left: configBtn
                focus: true

                text: "Run"
                onClicked: logicWrapper.run()
            }
        }
    }

    Dialog {
        id: configDialog
        width: 600
        title: "Configure"
        standardButtons: StandardButton.Save | StandardButton.Cancel

        GridLayout {
            width: parent.width
            columns: 3

            Text {
                text: "Executable path:"
            }
            TextField {
                id: binaryPathField
                Layout.fillWidth: true
                text: logicWrapper.configBinaryPath
            }
            Button {
                id: binaryButton

                Component.onCompleted: Layout.preferredWidth = modButton.width > width ? modButton.width : -1
                text: "Choose file..."

                onClicked: binaryFileDialog.open()

                FileDialog {
                    id: binaryFileDialog
                    title: "Choose binary"
                    selectFolder: false
                    selectMultiple: false
                    selectExisting: true
                    folder: binaryPathField.text + "/.."
                    onAccepted: {
                        var result = binaryFileDialog.fileUrl.toString()
                        binaryPathField.text = result.replace("file://", "")
                    }
                }
            }

            Text {
                text: "Mod path:"
            }
            TextField {
                id: modPathField
                Layout.fillWidth: true
                text: logicWrapper.configModPath
            }
            Button {
                id: modButton

                Component.onCompleted: Layout.preferredWidth = binaryButton.width > width ? binaryButton.width : -1
                text: "Choose folder..."

                onClicked: modFileDialog.open()

                FileDialog {
                    id: modFileDialog
                    title: "Choose mod folder"
                    selectFolder: true
                    selectMultiple: false
                    selectExisting: true
                    folder: modPathField.text
                    onAccepted: {
                        var result = modFileDialog.fileUrl.toString()
                        modPathField.text = result.replace("file://", "")
                    }
                }
            }
        }
        onAccepted: {
            logicWrapper.configBinaryPath = binaryPathField.text
            logicWrapper.configModPath = modPathField.text
            logicWrapper.savePlugins()
            logicWrapper.resetModels()
        }
    }

    MessageDialog {
        id: errorMsg
        title: "Error"
        icon: StandardIcon.Warning
        text: "Game could not launch."

    }

    Connections {
        target: logicWrapper
        onRunSucceeded: {
            logicWrapper.savePlugins()
            Qt.quit()
        }
        onRunFailed: {
            errorMsg.open()
        }
    }
}
