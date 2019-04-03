package com._360ec.ctf;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class SuperPass extends HttpServlet {
    Pattern p = Pattern.compile("flag\\{([0-9a-f]{32})\\}");

    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String secret = getServletContext().getInitParameter("secret");
        String token =request.getParameter("token");
        String msg = "Token错误!";
        if (token == null) {
            this.doGet(request, response);
            return;
        }

        Matcher tokenM = p.matcher(token.trim());
        if (!tokenM.matches()) {
            request.setAttribute("msg", msg);
            this.doGet(request, response);
            return;
        }

        if (secret.compareTo(this.genFlag(tokenM.group(1))) == 0) {
            msg = "Token输入正确!";
        }
        request.setAttribute("msg", msg);
        this.doGet(request, response);
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        RequestDispatcher view = request.getRequestDispatcher("WEB-INF/templates/login.jsp");
        view.forward(request, response);
    }

    private String genFlag(String token) {
        return "flag{" + token.substring(16, 32) + token.substring(8, 16) + token.substring(0, 8) + "}";
    }
}
