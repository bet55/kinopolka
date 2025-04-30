from adrf.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from classes import Tools, UserHandler, PostcardHandler, Invitation
import logging

# Configure logger
logger = logging.getLogger('kinopolka')

class InvitationViewSet(APIView):
    async def post(self, request: Request):
        """
        Send invitation for the next tea party.
        """
        try:
            invitation = Invitation()
            result = await invitation.send_invitation()
            logger.info("Invitation sent successfully")
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Failed to send invitation: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostCardViewSet(APIView):
    async def get(self, request: Request):
        """
        Retrieve the page with the current event's postcard.
        """
        try:
            users = await UserHandler.get_all_users()
            random_images = Tools.get_random_images()
            postcard, is_active = await PostcardHandler.get_postcard()

            # Берем активную открытку или пустой бланк
            postcard_url = (
                postcard.screenshot.url if is_active and postcard else random_images.get("postcard")
            )

            context = {
                "postcard": postcard_url,
                "random": random_images,
                "users": users,
                "is_active": is_active,
            }
            logger.info("Retrieved postcard page with is_active: %s", is_active)
            return render(request, "postcard.html", context=context)
        except Exception as e:
            logger.error("Failed to retrieve postcard page: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def post(self, request: Request):
        """
        Create a new postcard.
        """
        try:
            postcard_data, success = await PostcardHandler.create_postcard(request.data)
            if success:
                logger.info("Created new postcard successfully")
                return Response(data=postcard_data, status=status.HTTP_201_CREATED)
            logger.warning("Failed to create postcard: %s", postcard_data)
            return Response(data=postcard_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error creating postcard: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def put(self, request: Request):
        """
        Deactivate all postcards.
        """
        try:
            success = await PostcardHandler.deactivate_postcard()  # No need for postcard_id since update_all=True by default
            if success:
                logger.info("All postcards deactivated successfully")
                return Response(data={"message": "Postcards deactivated"}, status=status.HTTP_200_OK)
            logger.warning("Failed to deactivate postcards")
            return Response({"error": "Failed to deactivate postcards"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error deactivating postcards: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def delete(self, request: Request):
        """
        Delete a specific postcard.
        """
        try:
            postcard_id = request.data.get("id")
            if not postcard_id:
                logger.error("Missing postcard ID in delete request")
                return Response({"error": "Postcard ID required"}, status=status.HTTP_400_BAD_REQUEST)

            success = await PostcardHandler.delete_postcard(postcard_id)  # Updated to handle bool return
            if success:
                logger.info("Deleted postcard with id: %s", postcard_id)
                return Response(status=status.HTTP_204_NO_CONTENT)
            logger.warning("Failed to delete postcard with id: %s", postcard_id)
            return Response({"error": "Postcard not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error deleting postcard: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)