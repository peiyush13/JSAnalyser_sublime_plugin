import javax.swing.*;
import javax.swing.filechooser.FileNameExtensionFilter;
import java.io.File;
import java.util.Objects;

/**
 * Created by sachin on 2/5/17.
 */
public class FileSelector {

    public static void main(String [] args){

        if (args.length>1) {
            OpenDialogue("Rule File","js","Test");
        }else if (args.length==1){
            OpenDialogue("Test Rule Configuration file","json","Test");
        }else{
            OpenDialogue("Rule Configuration file","json","");
        }
    }

    public static void OpenDialogue(String description,String extension,String foldername){
        JFileChooser chooser;
        if (Objects.equals(foldername, "")){
            chooser = new JFileChooser(System.getProperty("java.class.path"));
        }else{
            chooser = new JFileChooser(System.getProperty("java.class.path")+ File.separator+foldername);
        }
        FileNameExtensionFilter filter = new FileNameExtensionFilter(description, extension);
        chooser.setFileFilter(filter);
        int returnVal = chooser.showOpenDialog(null);
        if (returnVal == JFileChooser.APPROVE_OPTION) {
            System.out.print(chooser.getSelectedFile().getAbsolutePath());
        }
    }

}