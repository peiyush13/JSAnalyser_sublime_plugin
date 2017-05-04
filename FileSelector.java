import javafx.application.Application;
import javafx.application.Platform;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

import javax.swing.*;
import javax.swing.filechooser.FileNameExtensionFilter;
import java.io.File;
import java.util.Objects;

/**
 * Created by sachin on 2/5/17.
 */
public class FileSelector extends Application {

    public static String args[];
    public static void main(String [] args){
        FileSelector.args=args;
        launch(args);
    }


    @Override
    public void start(Stage primaryStage) throws Exception {

        FileChooser fileChooser = new FileChooser();
        if (args.length>1) {
            fileChooser.setInitialDirectory(new File(System.getProperty("java.class.path")+File.separator+"Test"));
            fileChooser.setTitle("Rule File");
            fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Rule File","*.js"));
        }else if (args.length==1){
            fileChooser.setInitialDirectory(new File(System.getProperty("java.class.path")+File.separator+"Test"));
            fileChooser.setTitle("Test Rule Configuration file");
            fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Test Rule Configuration file","*.json"));
        }else{
            fileChooser.setInitialDirectory(new File(System.getProperty("java.class.path")));
            fileChooser.setTitle("Rule Configuration file");
            fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Rule Configuration file","*.json"));
        }


        File selectedFile = fileChooser.showOpenDialog(primaryStage);

        if (selectedFile != null) {
            System.out.print(selectedFile.getAbsolutePath());
        }
        Platform.exit();
    }
}