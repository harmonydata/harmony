package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import java.util.Map;
import org.apache.tika.Tika;
import java.io.ByteArrayInputStream;
import java.util.Base64;
import java.io.InputStream;
import org.apache.tika.exception.TikaException;
import org.apache.tika.metadata.Metadata;
import org.apache.tika.parser.ParseContext;
import org.apache.tika.parser.pdf.PDFParser;
import org.apache.tika.sax.BodyContentHandler;

// Handler value: example.HandlerString
public class HandlerString implements RequestHandler<Map<String, Object>, String>{

  @Override
  /*
   * Takes a String as input, and converts all characters to lowercase.
   */
  public String handleRequest(Map<String, Object> event, Context context)
  {
    LambdaLogger logger = context.getLogger();
    logger.log("EVENT TYPE: " + event.getClass().toString());
    logger.log("EVENT BODY: " + event.get("body").toString());
    logger.log("EVENT BODY TYPE: " + event.get("body").getClass().toString());

    try {
      byte[] decodedString = Base64.getDecoder().decode(event.get("body").toString().getBytes("UTF-8"));
      InputStream stream = new ByteArrayInputStream(decodedString);

      BodyContentHandler handler = new BodyContentHandler();
      Metadata metadata = new Metadata();
      ParseContext parseContext = new ParseContext();
      PDFParser pdfparser = new PDFParser();
      pdfparser.parse(stream,handler,metadata,parseContext);
      return handler.toString();


    } catch (Exception exception) {
      logger.log("Something went wrong.");
      logger.log("Your description here " + exception.toString());
      return exception.toString();
    }

  }
}