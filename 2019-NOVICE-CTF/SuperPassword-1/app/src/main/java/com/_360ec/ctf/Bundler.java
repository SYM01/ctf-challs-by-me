package com._360ec.ctf;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.*;


public class Bundler extends HttpServlet {
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String file;
        try {
            file = request.getParameter("file");
        } catch (NullPointerException e) {
            response.setStatus(404);
            return;
        }

        String[] fileList = file.split(",");
        int i = fileList[0].lastIndexOf('.');
        if (i > 0) {
            String ext = fileList[0].substring(i+1);
            switch (ext) {
                case "css":
                    response.setContentType("text/css");
                    break;
                case "js":
                    response.setContentType("application/javascript");
                    break;
            }
        }

        OutputStream writer = response.getOutputStream();
        byte[] buf = new byte[4096];
        int len;

        for (String fn:fileList) {
            File path = new File(this.getServletContext().getRealPath("resources"), fn);
            if (path.exists() && path.isFile()) {
                FileInputStream fis = new FileInputStream(path);
                while ((len = fis.read(buf)) > -1) {
                    writer.write(buf, 0, len);
                }
            }
        }
        writer.close();
    }
}
